from dotenv import dotenv_values
from instagramBot import instagramBot

def chooseAnOption():
	opciones = ["Guardar_registro_seguidores", "Comparar_registros"]
	while True:
		print("Por favor, elija una opción\n", "\n ".join(opciones))
		opcionElegida = input("\n$:")
		if (opcionElegida in opciones):
			return opcionElegida

if __name__ == "__main__":
	venv_dict = dict(dotenv_values(".env"))
	operacion = chooseAnOption()
	igBot = instagramBot(venv_dict["USERNAME"], venv_dict["PASSWORD"])	
	if (operacion == "Comparar_registros"): 
		igBot.compareFiles()
	else:
		igBot._login()
		if (operacion == "Guardar_registro_seguidores"): igBot.saveFollowersList()

