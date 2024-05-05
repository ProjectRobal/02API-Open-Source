'''
A react for poor men
'''

class HTMLBlock:

    def __init__(self):
        self._style:str=''
        self._classes:str=''

    def style(self,style:str or None=None)->str or None:
        if style is None:
            return self._style
        
        self._style=style

    def classes(self,classes:str or None=None)->str or None:
        if classes is None:
            return self._classes
        
        self._classes=classes

    def to_html(self)->str:
        raise NotImplementedError()
    
    def __str__(self):
        return self.to_html()
    

class DivBlock(HTMLBlock):
    def __init__(self,content:HTMLBlock or str):
        super().__init__()
        self.content=content

    def to_html(self)->str:
        return '<div style="{1}" class="{2}">{0}</div>'.format(self.content,self.style(),self.classes())
    

class HrefBlock(HTMLBlock):
    def __init__(self,content:HTMLBlock or str,href:str=""):
        super().__init__()
        self.content=content
        self._href=href

    def href(self,href:str or None=None)->str:
        if href is None:
            return self._href
        
        self._href=href

    def to_html(self) -> str:
        return '<a style="{1}" class="{2}" href="{3}">{0}</a>'.format(self.content,self.style(),self.classes(),self._href)
