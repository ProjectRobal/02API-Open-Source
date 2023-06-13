from common.pyhtml import HrefBlock

class HomeBlock(HrefBlock):
    def __init__(self, content:str, href: str = ""):
        super().__init__(content, href)
        self._classes="homeblock block"
    
    def classes(self,classes=None)->str:
        return self._classes


class MenuBlock(HrefBlock):
    def __init__(self, content:str, href: str = ""):
        super().__init__(content, href)
        self._classes="navblock"
    
    def classes(self,classes=None)->str:
        return self._classes

