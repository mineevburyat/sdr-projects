class FreqRange():
    def __init__(self, start, stop):
        if 5 < start <= 6000:
            self.start = start * 1e6
        else:
            raise ValueError
        if stop > start and 5 < stop <= 6000:
            self.stop = stop * 1e6
        else:
            raise ValueError
        
    def __repr__(self) -> str:
        return f"objFreqRange ({self.__str__()})"
        
    def __str__(self):
        return f"{round(self.start / 1e6, 0)} - {round(self.stop / 1e6, 0)} МГц"
    
    def inrange(self, freq):
        if self.start <= freq <= self.stop:
            return True
        return False
    
class FreqRanges():
    """FreqRanges((x,y)[,(x,y)...]) or FreqRanges(FreqRange()[, FreqRange()...])"""
    def __init__(self, *args):
        self.list = []
        self.empty = False
        if len(args) == 1:
            print(args[0], len(args[0]))
            if type(args[0] == FreqRange):
                self.list.append(args[0])
            if len(args[0]) == 2:
                self.list.append(FreqRange(args[0][0], args[0][1]))
            else:
                raise ValueError
        elif len(args) > 1:
            for arg in args:
                if type(arg) == FreqRange:
                    self.list.append(arg)
                    continue
                if len(arg) == 2:
                    self.list.append(FreqRange(arg[0], arg[1]))
                    continue
                else:
                    raise ValueError
            # 
        elif len(args) == 0:
            self.empty = True
            
                
    def __str__(self):
        if len(self.list) > 0:
            result = "\n"
        else:
            return 'empty frequency range list'
        l = [str(item) for item in self.list]
        return result.join(l)
    
    def inranges(self, freq):
        for range in self.list:
            if range.inrange(freq):
                return True
        return False
                
if __name__ == "__main__":
    fr_list = FreqRanges(FreqRange(100,150), FreqRange(430, 450))
    print(fr_list)
    print(fr_list.inranges(140000000))