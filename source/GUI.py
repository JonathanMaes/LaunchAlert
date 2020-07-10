import programenv as pe
import sys

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QTabWidget, QVBoxLayout, QPushButton, QTreeView
from PyQt5.Qt import QStandardItemModel, QStandardItem
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt

class GUI(QWidget):
    def __init__(self, app):
        self.QApp = QApplication(sys.argv) # Before super init because QWidget.__init__() requires a QApplication already running
        super().__init__()
        self.app = app
        self.width = 480
        self.height = 320
        
    def initUI(self):
        self.setWindowTitle(pe.PROGRAMNAME + ' ' + pe.VERSION)
        self.setGeometry(50,50,self.width,self.height) # TODO Change this to something relative to screen size

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        # Initialize tabs screen
        self.tabs = QTabWidget()
        self.grid.addWidget(self.tabs)
        self.tab1, self.tab2 = QWidget(), QWidget()
        self.tabs.resize(self.width, self.height)
        
        self.tabs.addTab(self.tab1, "Options")
        #self.tabs.addTab(self.tab2, "Tab 2")
        
        # Create first tab
        self.tab1.layout = QVBoxLayout(self)
        self.tab1.setLayout(self.tab1.layout)
        self.tab1_treeView = RocketTreeWidget(self.readRockets())
        self.tab1.layout.addWidget(self.tab1_treeView)


        self.show()
        self.QApp.exec_()
    
    def readRockets(self, path='data/rockets.csv'):
        '''
            @param path (str): 
            @return (dict): Tree with country -> provider -> family
        '''
        # Return nested dictionary of rockets, I guess
        with open(path) as inFile:
            data = [[field.strip() for field in line.strip().split(',')] for line in inFile][1:]
        
        blockedRockets = [] # TODO read this from self.app.options

        tree = {}
        for rocket in data:
            status = rocket[2]
            if status not in ['Active', 'Development']: # If the rocket is no longer in use, don't bother
                continue
            family = rocket[1]
            provider = rocket[3]
            country = rocket[4]
            if country not in tree: # If country not encountered yet, add it to dictionary
                tree[country] = {}
            if provider not in tree[country]: # If provider not encountered yet...
                tree[country][provider] = {}
            tree[country][provider][family] = family not in blockedRockets
        
        return tree
            
    
    def getOptions(self):
        return self.app.options


class RocketTreeWidget(QTreeView):
    def __init__(self, tree):
        super().__init__()
        self.setHeaderHidden(True)
        self.setAnimated(True)
        self.treeModel = QStandardItemModel()
        self.rootNode = self.treeModel.invisibleRootItem()
        self.setModel(self.treeModel)

 
        self.treeWidgets = {'country': {}, 'provider': {}, 'family': {}}
        self.rocketTree = tree
        for country in sorted(self.rocketTree):
            countryItem = RocketTreeItem(country, 'country')
            self.rootNode.appendRow(countryItem)
            self.treeWidgets['country'][country] = countryItem
            countryItem.setCheckState(Qt.Checked)
            countryItem.setCheckable(True)
            for provider in sorted(self.rocketTree[country]):
                providerItem = RocketTreeItem(provider, 'provider')
                countryItem.appendRow(providerItem)
                self.treeWidgets['provider'][provider] = providerItem
                providerItem.setCheckState(Qt.Checked)
                providerItem.setCheckable(True)
                providerItem.setAutoTristate(True)
                for family in sorted(self.rocketTree[country][provider]):
                    familyItem = RocketTreeItem(family, 'family')
                    providerItem.appendRow(familyItem)
                    self.treeWidgets['family'][family] = familyItem
                    familyItem.setCheckState(Qt.Checked)
                    familyItem.setCheckable(True)
        
        self.expandAll()

class RocketTreeItem(QStandardItem):
    def __init__(self, text, itemType):
        super().__init__()
        if itemType == 'country':
            fontSize, bold, color = 10, False, QColor(0, 0, 0)
        elif itemType == 'provider':
            fontSize, bold, color = 10, False, QColor(0, 0, 0)
        elif itemType == 'family':
            fontSize, bold, color = 10, False, QColor(0, 0, 0)

        fnt = QFont('Arial', fontSize)
        fnt.setBold(bold)
        self.setFont(fnt)

        self.setEditable(False)
        self.setForeground(color)
        self.setText(text)


if __name__ == '__main__':
    app = 0
    x = GUI(app)
    x.initUI()