from collections import UserDict
from datetime import datetime 
import json
import cmd

class Field:
    def __init__(self, value):
        self.value = value

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, new_value):
        self._value = new_value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        if not value or not value.strip():
            raise ValueError("Name cannot be empty.")
        super().__init__(value)

class Phone(Field):
    def validate(self, phone):
        return len(phone) == 10 and phone.isdigit()

    def __init__(self, value):
        if self.validate(value):
            super().__init__(value)
        else:
            raise ValueError
        
    @Field.value.setter
    def value(self, new_value):
        if self.validate(new_value):
            self._value = new_value
        else:
            raise ValueError("Invalid phone number")
        
class Birthday(Field):
    def validate(self, Birthday):
        try:
            datetime.strptime(Birthday, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def __init__(self, value):
        if self.validate(value):
            super().__init__(value)
        else:
            raise ValueError("Invalid birthday format")

    @Field.value.setter
    def value(self, new_value):
        if self.validate(new_value):
            self._value = new_value
        else:
            raise ValueError("Invalid birthday format")

class Record:
    def __init__(self, name, Birthday = None):
        self.name = Name(name)
        self.Birthday = Birthday
        self.phones = []

    def days_to_birthday(self):
        today = datetime.now()
        if self.Birthday:
            next_birthday = self.Birthday.replace(year=today.year)
            if today > next_birthday:
                next_birthday = self.Birthday.replace(year=today.year + 1)
            delta_days = (next_birthday - today).days
            return delta_days
        else:
            return None

    def add_phone(self, phone_number: str):
        phone = Phone(phone_number)
        phone.validate(phone_number)
        if phone not in self.phones:
            self.phones.append(phone)

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
    
    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                self.remove_phone(old_phone)
                self.add_phone(new_phone)
                return 
            raise ValueError(f"Phone {old_phone} not found in record.")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):
    
    def search(self, search_string):
        results = []
        for record in self.data.values():
            if (
                search_string.lower() in record.name.value.lower()
                or any(search_string in phone.value for phone in record.phones)
            ):
                results.append(record)
        return results

    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def iterator(self, item_number):
        counter = 0
        result = ''
        for item, record in self.data.items():
            result += f'{item}: {record}'
            counter += 1
            if counter >= item_number:
                yield result
                counter = 0
                result = ''
    
    def dump(self):
        with open(self.file, 'wb') as file:
            json.dump((self.record_id, self.record), file)

    def load(self):
        if not self.file.exists():
            return
        with open(self.file, 'rb') as file:
            self.record_id, self.record = json.load(file)


class Controller(cmd.Cmd):
    def __init__(self):
        super().__init__()
        self.prompt = "AddressBook> "
        self.address_book = AddressBook("address_book.json")

    def do_search(self, line):
        search_string = input("Введіть рядок пошуку: ")
        search_results = self.address_book.search(search_string.strip())
        if search_results:
            print("Результати пошуку:")
            for result in search_results:
                print(result)
        else:
            print("Контакти не знайдено.")

    def do_quit(self, line):
        self.address_book.dump()
        return True

if __name__ == "__main__":
    controller = Controller()
    controller.cmdloop()