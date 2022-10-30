from bs4 import BeautifulSoup


class Tasks:
    
    __struct: BeautifulSoup
    
    def __init__(self, html: bytes) -> None:
        self.__struct = BeautifulSoup(html)
        
    