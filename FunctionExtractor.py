#  Requires win32k.c to work(Needs to be in the same folder. )
#  For a given list of functions, it will look through the win32k file to find out what functions can that function call


class Node:
    allNodes = {} # Class Var
    def __init__(self, name):
        self.name = name
        self.children = [] # List of all the children names (not the child node)
        Node.allNodes[name] = self
    def addChild(self, c):
        self.children.append(c)
    @classmethod
    def getNode(cls, n):
        try:
            return cls.allNodes[n]
        except KeyError:
            print 'Error getting %s node'%(n)
            return
    @classmethod
    def enumNode(cls, func, maxDepth=5, depth=0):
        print ' |' * depth + func
        if depth >= maxDepth:
            return
        n = cls.getNode(func)
        for child in n.children:
            cls.enumNode(child, maxDepth=maxDepth, depth=depth+1)
    @classmethod
    def enumNode2(cls, func, maxDepth=5, depth=0):
        print ' |' * depth + func
        if depth >= maxDepth:
            return
        n = cls.getNode(func)
        for child in n.children:
            cls.enumNode2(child, maxDepth=maxDepth, depth=depth+1)
        if n.children:
            print ' |' * depth + func


class FunctionExtractor:
    listOfFunctions = [
        # 'ValidUmpdHooks'
        'NtGdiCreateHatchBrushInternal',
        # 'NtGdiSetBrushAttributes',
        # 'NtGdiClearBrushAttributes',
        # 'NtGdiDeleteObjectApp',
    ]

    def __init__(self,listOfFunctions=[]):
        if listOfFunctions:
            if isinstance(listOfFunctions,list):
                FunctionExtractor.listOfFunctions = listOfFunctions
            else:
                print 'Please enter a proper list of functions'

    def start(self):
        filenames = ['win32k.c']
        lines = []
        for filename in filenames:
            try:
                f = open(filename,'r')
                for line in f.read().splitlines():
                    lines.append(line)
                f.close()
            except IOError:
                print 'Error. File %s not found'%(filename)
                return
        knownfails = (
            'return',
            'if',
            'else',
            'void',
            'abs',
            'while',
            'for',
            'mode',
            'int',
            'switch',
            'PVOID',
            'JUMPOUT',
            'HIBYTE',
            'HIWORD',
            'HIDWORD',
            'SHIDWORD',
            'SLOBYTE',
            '__OFADD__',
            '__OFSUB__',
            '__CFADD__',
        )
        dic={}  # Stores the function name as well as that function's index
        for i in range(len(lines)):
            line = lines[i]
            line = line.replace('(_','_')
            if ';' not in line and ('call' in line or 'int __' in line or '__userpurge' in line or '::' in line) and line.strip()[0] not in '([{':
                funcName = line.split('<')[0].split('(')[0].split()[-1]
                dic[funcName] = i

        #  For each function, create a node
        ll = FunctionExtractor.listOfFunctions[:]
        for func in ll:
            currentNode = Node(func)
            try:
                i = dic[func]
                openBraces = lines[i].count('{')
            except KeyError:
                # print 'Error: %s is not in win32k'%(func)
                continue

            #  Go to the function and parse to lines to extract the functions called by this function
            #  Add those function names to the children of the current function node
            while True:
                try:
                    i += 1
                    line = lines[i]
                except IndexError:
                    print '%s infinite error' % (func)
                    break

                if '"' not in line and "'" not in line:
                    openBraces += line.count('{')
                    openBraces -= line.count('}')

                if openBraces==0:
                    break

                if not (line.count('(')) or line.strip()[0] in '/':
                    continue

                try:
                    wantedPart = line.split(';')[0].split('=')[-line.count('=')].replace('if (','').replace('!','')
                    if len(wantedPart.split('('))==1:
                        continue
                    funcName = wantedPart.split('(')[0].split()[-1].strip()

                    if (funcName.translate(None,'_:~').isalpha()) and funcName not in knownfails:
                        # for j in knownfails:
                        #     if func==j:
                        #         print "wow this isn't suppose to happen"
                        #         print line
                        # if funcName=='~HIWORD':
                        #     print line
                        currentNode.addChild(funcName)
                        if  funcName not in ll:
                            ll.append(funcName)
                except:
                    continue

if __name__ == "__main__":
    listOfFunctions = [
    # 'NtGdiCreateHatchBrushInternal',
    'NtGdiSetBrushAttributes',
    # 'NtGdiClearBrushAttributes',
    # 'NtGdiDeleteObjectApp',
]

    FunctionExtractor(listOfFunctions).start()
    for func in listOfFunctions:  # Can just enumerate one function
        Node.enumNode(func,5)


