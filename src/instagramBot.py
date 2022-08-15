from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import datetime
from time import sleep
import subprocess
import platform
import selenium
import os
import json

class instagramBot:
	humanRestTime = 3 # seconds. Cantidad de tiempo entre operaciones para engañar a instagram
	rootURL = "https://www.instagram.com/"
	def __init__(self, username, password):
		self.username = username
		self.password = password
		self.followersQuantity = 0
		self.followersDict = {}
		self.webDriver = None
		# self._login()
	
	def _generateDirPath(self, dirName):
		OSname = platform.system()
		dirSeparator = "\\" if (OSname == "Windows") else "/"
		return dirSeparator.join([".", dirName]) + dirSeparator

	def setupWebDriver(self):
		# EJECUTAR EL DRIVER QUE ABRIRÁ EL NAVEGADOR
		driverDir = self._generateDirPath("driver")
		driverFullPath = driverDir + os.listdir(driverDir)[0]
		# RETORNAR EL OBJETO QUE REPRESENTA EL WEBDRIVER PARA USAR SUS METODOS
		return selenium.webdriver.Firefox(executable_path=driverFullPath)

	def _clickTargetButton(self, xpathStr):
		buttonToClick = self.webDriver.find_element(By.XPATH, xpathStr)
		buttonToClick.click()

	def _sendValuesToInput(self, valueToSend, xpathStr):
		valueFormBox = self.webDriver.find_element(By.XPATH, xpathStr)
		valueFormBox.send_keys(valueToSend)

	def _typeCredentials(self):
		xpathUsernameFormBox = "/html/body/div[1]/section/main/article/div[2]/div[1]/div[2]/form/div/div[1]/div/label/input"
		xpathPasswordFormBox = "/html/body/div[1]/section/main/article/div[2]/div[1]/div[2]/form/div/div[2]/div/label/input"
		self._sendValuesToInput(self.username, xpathUsernameFormBox)
		sleep(self.humanRestTime)
		self._sendValuesToInput(self.password, xpathPasswordFormBox)
		sleep(self.humanRestTime)
		xpathLoginButton = "/html/body/div[1]/section/main/article/div[2]/div[1]/div[2]/form/div/div[3]/button"
		self._clickTargetButton(xpathLoginButton)
		sleep(self.humanRestTime)

	# IR A LA PAGINA DE LOGIN
	def _login(self):
		self.webDriver = self.setupWebDriver()
		self.webDriver.get(self.rootURL)
		sleep(self.humanRestTime*1.5)
		self._typeCredentials()
		sleep(self.humanRestTime)

	def saveFollowersList(self):
		# NECESARIO PARA SABER CUANTOS SEGUIDORES HAY Y ASÍ, PODER DETERNERNOS AL ITERAR SOBRE ESTOS
		self.webDriver.get(self.rootURL + self.username)
		sleep(self.humanRestTime)
		xpathFollowersNumber = "/html/body/div[1]/div/div/div/div[1]/div/div/div/div[1]/div[1]/section/main/div/header/section/ul/li[2]/a/div/span"		
		rawText = self.webDriver.find_element(By.XPATH, xpathFollowersNumber)
		self.followersQuantity = int(rawText.get_attribute('innerText'))	

		# Ir al modal de los seguidores
		self.webDriver.get(self.rootURL + self.username + "/followers")
		sleep(self.humanRestTime)

		# Focus en el modal de los seguidores para poder hacer SCROLL DOWN
		xpathModalBody = "/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div/div[2]"
		self._scrollDownSection(xpathModalBody)
		sleep(self.humanRestTime/2)

		# Guardar el dict de los seguidores (username:KEY para acceso eficiente) como JSON para escribirlo en un fichero txt
		self._writeFollowersToTextFile()

	def _scrollDownSection(self,scrollableBodyXpath):
		print("Scrolling down...")
		scrollableBody = self.webDriver.find_element(By.XPATH, scrollableBodyXpath)
		while True:
			scrollableBody.send_keys(Keys.PAGE_DOWN)
			sleep(self.humanRestTime/20)
			# BUSCAMOS DETENERNOS AL LLEGAR AL ULTIMO SEGUIDOR (QUE ES EL NUMERO n OBTENIDO ANTERIORMENTE)
			if (self._checkLastFollowerWasFound()):
				break
		print("END REACHED")
		self._saveFollowersToDict()

	def _checkLastFollowerWasFound(self):
		xpathLastFollower = f"/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div/div[2]/div[1]/div/div[{self.followersQuantity}]"
		try:
			self.webDriver.find_element(By.XPATH, xpathLastFollower)
			return True
		except:
			return False

	def _saveFollowersToDict(self):
		# OBTENEMOS UNA LISTA DE TODOS LOS SEGUIDORES QUE SON REPRESENTADOS POR UNA FILA (div en realidad)
		# FUNCIONA PORQUE YA CARGAMOS EN EL DOM TODOS LOS SEGUIDORES (sus respectivos divs) AL HACER SCROLL DOWN
		xpathFollowersList = f"/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div/div[2]/div[1]/div/div"
		followersList = self.webDriver.find_elements(By.XPATH, xpathFollowersList)
		for follower in followersList:
			followerUsername = follower.get_attribute('innerText').split("\n")[0]
			if (followerUsername not in self.followersDict):
				self.followersDict[followerUsername] = 0
			self.followersDict[followerUsername] +=1
		print("Total seguidores: ",len(followersList))

	def _writeFollowersToTextFile(self):
		jsonedDict = json.dumps(self.followersDict)
		reportTime = str(datetime.now()).split(" ")
		reportName = "reporteIg#" + reportTime[0] + "#" + "'".join(reportTime[1][0:8].split(':'))+ ".txt"
		reportsDir = self._generateDirPath("reports")
		print(reportName)
		self._writeJsonToFile(jsonedDict, reportsDir + reportName)

	def _writeJsonToFile(self, jsonStr, filePath):
		with open(filePath, 'w') as f:
			f.write(jsonStr)

	#----------------------------------------------------------------------------------------------

	def _getDictJsonFromFile(self, filePath):
		with open(filePath) as jsonFile:
			jsonValue = jsonFile.readlines()
			if (len(jsonValue) < 1):
				return {}
			return json.loads(jsonValue[0])

	def _printRegistrosFiles(self, listaArchivos):
		for index, nombreArchivo in enumerate(listaArchivos):
			splittedName = nombreArchivo.split("#")
			print(f"Index:{index}\t\tDia registro: {splittedName[1]}\tHora registro: {splittedName[2]}")
		
	def _getGoodIndexInput(self, maxIndex, posicion):
		while True:
			try:
				inputIndex = int(input(f"Ingresar {posicion} índice: "))
				if (inputIndex > -1 and inputIndex < maxIndex):
					return inputIndex
				raise ValueError
			except:
				print("Ingresar un indice válido\n")

	def compareFiles(self):
		reportsDir = self._generateDirPath("reports")
		listaArchivos = os.listdir(reportsDir)
		if (len(listaArchivos) < 2):
			print("Error. Obtener al menos dos archivos de registro")
			return
		self._printRegistrosFiles(listaArchivos)
		indexFile1 = self._getGoodIndexInput(len(listaArchivos), "primer")
		indexFile2 = self._getGoodIndexInput(len(listaArchivos), "segundo")
		if (indexFile1 == indexFile2):
			print("Error. Elegir indices distintos")
			return
		if (indexFile1 > indexFile2):
			aux = indexFile1
			indexFile1 = indexFile2
			indexFile2 = aux
		self._compareJsons(reportsDir, listaArchivos, indexFile1, indexFile2)

	def _compareJsons(self, reportsDir, listaArchivos, index1, index2):
		dictPrevious = self._getDictJsonFromFile(reportsDir + listaArchivos[index1])
		dictAfter = self._getDictJsonFromFile(reportsDir + listaArchivos[index2])
		print(f"\nComparando el archivo ANTIGUO {listaArchivos[index1]} \ncontra el archivo RECIENTE {listaArchivos[index2]}\n")
		# CHEQUEANDO NUEVOS UNFOLLOWERS
		self._checkFollowersVariations("gente que te dejó de seguir", dictPrevious, dictAfter)

		# CHEQUEANDO NUEVOS FOLLOWERS
		self._checkFollowersVariations("nuevos seguidores", dictAfter, dictPrevious)

	def _checkFollowersVariations(self, messagePrefix, baseDict, toCheckDict):
		namesToCheckList = baseDict.keys()
		variationsList = []
		for nameKey in namesToCheckList:
			if (nameKey not in toCheckDict):
				variationsList.append(nameKey)
		print(f"Cantidad de {messagePrefix}: {len(variationsList)}")
		print(variationsList, '\n')