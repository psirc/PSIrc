class PasswordHandler:
    def __init__(self, filename: str) -> None:
        self._filename = filename
        self._passwords = {"I": {}, "C": {}, "N": {}}
        self._oper_credentials = dict()

    @staticmethod
    def _valid_i_host(data: str) -> bool:
        data_list = data.split("@")
        if len(data_list) != 2:
            return False
        return True

    @classmethod
    def valid_host(cls, type: str, data: str) -> bool:
        if type == "I":
            return cls._valid_i_host(data)
        else:
            return True

    @classmethod
    def valid_operator(cls, type: str, data: str) -> bool:
        pass

    def _valid_password(self, address: str, password: str) -> bool:
        return not self._passwords["I"][address] or self._passwords["I"][address] == password

    def valid_password(self, address: str, password: str) -> bool:
        hostname, address = address.split("@")
        addr_list = address.split(".")

        for password_address_full in self._passwords["I"].keys():
            password_hostname, password_addr = password_address_full.split("@")
            valid_parts = 0
            passwd_addr_list = password_addr.split(".")
            for idx, passwd_addr_element in enumerate(passwd_addr_list):
                if idx > len(addr_list) - 1:
                    break
                if passwd_addr_element == "*":
                    valid_parts = len(passwd_addr_list)
                    break
                elif addr_list[idx] == passwd_addr_element:
                    valid_parts += 1
                    continue
                break
            if valid_parts == len(passwd_addr_list):
                if password_hostname == "*" or password_hostname == hostname:
                    return self._valid_password(password_address_full, password)
        return False

    def parse_config(self) -> None:
        with open(self._filename, "r") as fp:
            lines = fp.readlines()
            for line in lines:
                type = line[0]
                if type == "#":
                    continue
                if type not in "ICN" or line[1] != ":":
                    continue
                line = line.split("#")[0].rstrip()  # strip comments
                line_list = line[2:].split(":")  # split into parts
                if self.valid_operator(type, line_list[0]):
                    pass
                elif not self.valid_host(type, line_list[0]):
                    continue
                self._passwords[type][line_list[0]] = line_list[1] if line_list[1] else None
        print("passwords set")
