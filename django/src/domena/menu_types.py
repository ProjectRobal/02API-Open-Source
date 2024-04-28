from common.pyhtml import HrefBlock,DivBlock

class HomeBlock(HrefBlock):
    def __init__(self, content:str, href: str = ""):
        super().__init__(content, href)
        self._classes="homeblock block"
    
    def classes(self,classes=None)->str:
        return self._classes


class MenuBlock(HrefBlock):
    def __init__(self, content:str, href: str = ""):
        _content=DivBlock(content)
        _content.classes("navblock")
        super().__init__(_content, href)
    
    def classes(self,classes=None)->str:
        return self._classes

