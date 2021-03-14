import os,subprocess,time
from datetime import datetime
from zipfile import ZipFile,ZIP_DEFLATED
from shutil import rmtree
from PyQt5 import QtCore, QtGui, QtWidgets





class Ui_Dialog():
    def __init__(self):
        self.outputDir = "tempOutput"
        self.outputModDir = "packagerOutput"
        self.backupDir = "backup"
        self.backupZipDir = "backupZIP"
        # self.inputDir = input("Input directory : ")
        self.fileName = ""
        # self.changeDir = inputDir.split(fileName)[0]
        self.fileModList = []
        self.timeDate = datetime.now().strftime("%Y%m%d_%H%M%S_")
        self.User = "lowaccess"
        self.AccessKey = "AKIAYCTPYTZAGOETVGNK"
        self.SecretKey = "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"
        self.BucketName = "moldhole"
    def writeLogFile(self):
        if(not os.path.isdir(self.backupDir)):
            os.makedirs(self.backupDir)
        modName = self.outputModDir.split("\\")[-1]
        modDate = datetime.now().strftime("%Y,%m,%d %H:%M:%S")
        logFile = open(self.backupDir+"\\"+self.timeDate+"log.txt", 'w')
        logFile.write("Modded with : " +modName+" on "+modDate+"\n")
        for file in self.fileModList:
            logFile.write(file+"\n")
        logFile.close()
    def checkForConflict(self):
        self.logText.append("Checking for compatibilities ...")
        for root, dirs, files in os.walk(self.outputDir):
            for fileName in files:
                if("_log.txt" in fileName):
                    #print("fileName : ",os.path.join(root, fileName))
                    with open(os.path.join(root, fileName),"r") as logFile:
                        data = logFile.readlines()
                        logFile.close()
        for line in self.fileModList:
            #print("line : ",line)
            for item in data:
                #print("item : ",item)
                if(line in item):
                    return False
        return True
    def extractISOFile(self,isoDir):
        #," && wit", "extract "+inputDir, " --dest " +outputDir
        proc = os.popen("wit extract \""+ isoDir + "\" --dest "+ self.outputDir)
        output = proc.read()
        self.logText.append(output)

    def zipISOFile(self):
        self.fileName = self.inputBase.toPlainText().replace("/","\\").split("\\")[-1].replace(" ","")

        moddedFileName = self.timeDate+"Modded_"+self.fileName
        proc = os.popen("wit copy \"" + self.outputDir + "\" --dest " +  moddedFileName)
        output = proc.read()
        self.logText.append(output)

    def zipdir(self,path, ziph):
        # ziph is zipfile handle
        
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))
    #Method for calling zipdir method and name the output zip file
    def zipBackup(self,folder):
        
        zipName = self.timeDate+self.backupDir+ ".zip"
        # create a ZipFile object
        zipf = ZipFile(zipName, 'w', ZIP_DEFLATED)
        self.zipdir(folder, zipf)
        zipf.close()
        if(not os.path.isdir(self.backupZipDir)):
            os.makedirs(self.backupZipDir)
        os.popen("move " + zipName +" "+self.backupZipDir)

    def extractFile(self,absZipPath,outputDir):
        
        with ZipFile(absZipPath, 'r') as zip_ref:
            zip_ref.extractall(outputDir)
        self.logText.append("Extracting Done!")
    def listAllModFiles(self):
        for root, directories, files in os.walk(self.outputModDir):
            for fileName in files:
                # Join the two strings in order to form the full filepath.
                filepath = os.path.join(root, fileName)
                self.fileModList.append(filepath)  # Add it to the list.
                #print(filepath)
    def copyBackUpFiles(self):
        if(not os.path.isdir(self.backupDir)):
            os.makedirs(self.backupDir)
        #Looping through the base game for backup files to be replaced 
        self.writeLogFile()
        if(os.path.isdir(self.outputDir+"\\DATA")): 
            self.outputDir = self.outputDir+"\\DATA"
            #print("self.outputDir ", self.outputDir)
        for file in self.fileModList:
            fileToBackup =self.outputDir + file.split(self.outputModDir)[1]
            #print("fileToBackup: ",fileToBackup)
            try:
                # Getting the destination in backup folder for copying
                desDir = self.backupDir+file.split(self.outputModDir)[1].replace(file.split(self.outputModDir)[1].split("\\")[-1],"")
                # print("desDir: ",desDir)
                if(not os.path.isdir(desDir)):
                    os.makedirs(desDir)
                os.popen("copy \"" + fileToBackup +"\" "+desDir )
            except:
                continue
        time.sleep(1)
        #Call Function to zip the backup folder and move to backupZIP folder
        self.zipBackup(self.backupDir)
        time.sleep(1)
        #Delete backup folder
        try:
            rmtree(self.backupDir)
        except:
            self.logText.append("Can't find Backup Folder")
            pass
        self.logText.append("Backup Done!")
    def checkForUpdate(self):
        pass

    def revertToBaseVersion(self):
        #extract latest backup zip file and replace those file from self.backupDir to self.outputDir
        #get latest backupfile
        
        tempListInt = []
        tempListStr = []
        for root, dirs, files in os.walk(self.backupZipDir):
            for file in files:
                if(".zip" in file):
                    tempListInt.append(int(file.split("_backup.zip")[0].replace("_","")))
                    tempListStr.append(os.path.join(root,file))
        lastestFile = tempListInt.index(max(tempListInt))
        tempFile = tempListStr[lastestFile]
        time.sleep(2)
        self.extractFile(tempFile,"")
        #Copy to all backup to game folder
        os.popen("Xcopy /E /H /I "+ "backup \""+self.outputDir + "\" /Y")
        self.logText.append("Reverting Done!")
        time.sleep(1)
        #Delete backup folder
        try:
            rmtree(self.backupDir)
            #print("Here")
        except:
            self.logText.append("Can't find Backup Folder")
            pass
    def installMod(self):
        #Check for update by comparing with updatelog, if there is update, download, else skip revert

        #revert to original of base game from latest backup file

        #Go self.outputModDir copy all files to base game
        #/E – This option makes sure that empty subfolders are copied to the destination.
        #/H - Copy files with hidden and system file attributes
        #/I – Avoids prompting if the destination is a folder or file.
        self.logText.append("Installing new mod...")
        time.sleep(1)
        os.popen("Xcopy /E /H /I \"" + self.outputModDir +"\" \""+self.outputDir +"\" /Y")
        self.logText.append("Done!")
    def cleanUpTempFolder(self):
        pass
    def setupUi(self, Dialog):
        #Setup main Dialog
        Dialog.setObjectName("Dialog")
        Dialog.setEnabled(True)
        Dialog.setFixedSize(563, 339)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setAutoFillBackground(False)
        Dialog.setSizeGripEnabled(False)

        self.browseBox = QtWidgets.QGroupBox(Dialog)
        self.browseBox.setGeometry(QtCore.QRect(10, 10, 531, 91))
        self.browseBox.setTitle("")
        self.browseBox.setObjectName("browseBox")

        self.baseText = QtWidgets.QLabel(self.browseBox)
        self.baseText.setGeometry(QtCore.QRect(10, 20, 131, 21))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.baseText.setFont(font)
        self.baseText.setObjectName("baseText")

        self.baseBtn = QtWidgets.QPushButton(self.browseBox)
        self.baseBtn.setGeometry(QtCore.QRect(440, 20, 75, 23))
        self.baseBtn.setObjectName("baseBtn")
        self.baseBtn.clicked.connect(self.browserBase)

        self.modText = QtWidgets.QLabel(self.browseBox)
        self.modText.setGeometry(QtCore.QRect(10, 50, 111, 21))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.modText.setFont(font)
        self.modText.setObjectName("modText")

        self.modBtn = QtWidgets.QPushButton(self.browseBox)
        self.modBtn.setGeometry(QtCore.QRect(440, 50, 75, 23))
        self.modBtn.setObjectName("modBtn")
        self.modBtn.clicked.connect(self.browserMod)

        self.inputBase = QtWidgets.QTextEdit(self.browseBox)
        self.inputBase.setGeometry(QtCore.QRect(140, 20, 291, 21))
        self.inputBase.setObjectName("inputBase")

        self.inputMod = QtWidgets.QTextEdit(self.browseBox)
        self.inputMod.setGeometry(QtCore.QRect(140, 50, 291, 21))
        self.inputMod.setObjectName("inputMod")

        self.showBox = QtWidgets.QGroupBox(Dialog)
        self.showBox.setGeometry(QtCore.QRect(10, 110, 411, 221))
        self.showBox.setTitle("")
        self.showBox.setObjectName("showBox")

        self.logText = QtWidgets.QTextEdit(self.showBox)
        self.logText.setGeometry(QtCore.QRect(10, 40, 371, 141))
        self.logText.setObjectName("logText")
        self.logText.setReadOnly(True)
        self.progressText = QtWidgets.QLabel(self.showBox)
        self.progressText.setGeometry(QtCore.QRect(10, 0, 141, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.progressText.setFont(font)
        self.progressText.setObjectName("progressText")

        self.updateBtn = QtWidgets.QPushButton(Dialog)
        self.updateBtn.setGeometry(QtCore.QRect(440, 120, 101, 91))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.updateBtn.setFont(font)
        self.updateBtn.setObjectName("updateBtn")
        self.updateBtn.clicked.connect(self.patchAction)

        self.revertBtn = QtWidgets.QPushButton(Dialog)
        self.revertBtn.setGeometry(QtCore.QRect(440, 230, 101, 91))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.revertBtn.setFont(font)
        self.revertBtn.setObjectName("revertBtn")
        self.revertBtn.clicked.connect(self.revertAction)

        self.progressBar = QtWidgets.QProgressBar(self.showBox)
        self.progressBar.setGeometry(QtCore.QRect(10, 190, 405, 23))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        #Popup message for Done
        self.msgInfor = QtWidgets.QMessageBox()
        self.msgInfor.setIcon(QtWidgets.QMessageBox.Information)
        self.msgInfor.setText("Done!")
        self.msgInfor.setWindowTitle("Result")
        #Popup message for Warning
        self.msgWarn = QtWidgets.QMessageBox()
        self.msgWarn.setIcon(QtWidgets.QMessageBox.Warning)
        self.msgWarn.setText("Warning!This mod will overwrite old mods!")
        self.msgWarn.setWindowTitle("Result")
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.baseText.setText(_translate("Dialog", "Game ISO File"))
        self.baseBtn.setText(_translate("Dialog", "Browse"))
        self.modText.setText(_translate("Dialog", "Mod Zip File"))
        self.modBtn.setText(_translate("Dialog", "Browse"))
        self.logText.setHtml(_translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.progressText.setText(_translate("Dialog", "Progress Log"))
        self.updateBtn.setText(_translate("Dialog", "UPDATE"))
        self.revertBtn.setText(_translate("Dialog", "REVERT"))
    #Method for browsing the Base Directory
    def browserBase(self):
        data_path =QtWidgets.QFileDialog.getOpenFileName(None, 'Select ISO file...', os.getcwd())[0]
        if(".iso" in data_path):
            try:
                self.inputBase.setText(data_path)
            except:
                pass
        else:
            self.logText.append("Wrong File Format")
    #Method for browsing the Modded Directory
    def browserMod(self):
        data_path =QtWidgets.QFileDialog.getOpenFileName(None, "Select Mod file...",os.getcwd())[0]
        if(".zip" in data_path):
            try:
                self.inputMod.setText(data_path)
            except:
                pass
        else:
            self.logText.append("Wrong File Format")
    def revertAction(self):
        #self.logText.append("Reverting Base Game back to original...")
        #self.revertToBaseVersion()
        self.progressBar.setValue(100)

    def patchAction(self):
        #Extract Iso File
        try:
            self.extractISOFile(self.inputBase.toPlainText().replace("/","\\"))
            self.progressBar.setValue(10)
        except Exception as e:
            self.logText.append("Error in Extracting ISO file!")
            self.logText.append(e.__class__,"occurred.")
            pass
        #Extract Mod File
        try:
            self.logText.append("Extracting file: %s ..."%self.inputMod.toPlainText())
            self.extractFile(self.inputMod.toPlainText().replace("/","\\"),"")
            self.progressBar.setValue(20)
        except Exception as e:
            self.logText.append("Error in Extracting Mod file!")
            self.logText.append(e.__class__,"occurred.")
            pass
        try:
            self.listAllModFiles()
            self.progressBar.setValue(30)
        except Exception as e:
            self.logText.append("Error in Extracting Mod file!")
            self.logText.append(e.__class__,"occurred.")
            pass
        if(self.checkForConflict()):
            self.progressBar.setValue(40)
            try:
                self.logText.append("Backing up base game file changes ...")
                self.copyBackUpFiles()
                self.progressBar.setValue(50)
            except Exception as e:
                self.logText.append("Error in Backing up file!")
                self.logText.append(e.__class__,"occurred.")
                pass
            try:
                self.installMod()
                self.progressBar.setValue(80)
            except Exception as e:
                self.logText.append("Error in Installing mod!")
                self.logText.append(e.__class__,"occurred.")
                pass
            try:
                #Convert back to .iso
                self.zipISOFile()
                self.progressBar.setValue(100)
                self.msgInfor.exec_()
            except Exception as e:
                self.logText.append("Error in Zipping ISO file!")
                self.logText.append(e.__class__,"occurred.")
                pass
        else:
            self.logText.append("")
            self.msgWarn.exec_()
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

 