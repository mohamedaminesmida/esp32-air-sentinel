from machine import Pin, ADC, I2C, PWM
import time
import json
import dht
import ssd1306

# ----------------------------------------------------
# Configuration matérielle (ESP32)
# ----------------------------------------------------
# 1. Capteur analogique de gaz (GPIO 34)
capteur_gaz = ADC(Pin(34))
capteur_gaz.atten(ADC.ATTN_11DB)

# 2. Capteur température & humidité DHT22 (GPIO 15)
capteur_dht = dht.DHT22(Pin(15))

# 3. Buzzer sonore (GPIO 27)
buzzer = PWM(Pin(27))
buzzer.duty(0)  # Silence au démarrage

# 4. Écran OLED SSD1306 I2C (SDA=GPIO 21, SCL=GPIO 22)
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Tableau pour stocker les 10 dernières mesures de gaz
t = []
temp = 24.0
hum = 50.0

# ----------------------------------------------------
# Signal Processing & Alarm Logic
# ----------------------------------------------------
def calculer_moyenne(t):
    """Fonction qui calcule la moyenne du tableau t"""
    s = 0
    for i in range(len(t)):
        s = s + t[i]
    return s // len(t)


def emettre_son(nombre_bips, duree_ms, frequence):
    """Procédure pour émettre des bips sonores avec le buzzer"""
    for _ in range(nombre_bips):
        buzzer.freq(frequence)
        buzzer.duty(512)
        time.sleep_ms(duree_ms)
        buzzer.duty(0)
        time.sleep_ms(duree_ms)


def gerer_alarme(ppm):
    """Procédure pour gérer le buzzer selon le niveau de gaz"""
    if ppm >= 700:
        etat = "CRITICAL"
        emettre_son(3, 70, 2500)   # 3 bips rapides et aigus (danger)
    elif ppm >= 300:
        etat = "WARNING"
        emettre_son(1, 120, 1500)  # 1 bip modéré (attention)
    else:
        etat = "SAFE"
        buzzer.duty(0)             # Silence
    
    return etat


def afficher_ecran(ppm, temp, hum, etat):
    """Procédure pour afficher les données sur l'écran OLED"""
    oled.fill(0)
    
    oled.text("=== AIR SENTINEL ===", 0, 0)
    oled.text("Gaz : " + str(ppm) + " PPM", 0, 16)
    oled.text("Temp: " + str(temp) + " C", 0, 28)
    oled.text("Hum : " + str(hum) + " %", 0, 40)
    oled.text("Etat: " + etat, 0, 52)
    
    oled.show()


# ----------------------------------------------------
# Programme Principal
# ----------------------------------------------------
compteur = 0

while True:
    # 1. Lecture du capteur de gaz
    val = capteur_gaz.read()
    t.append(val)
    if len(t) > 10:
        t.pop(0)
    
    moy = calculer_moyenne(t)
    ppm = int((moy / 4095) * 1000)
    
    # 2. Lecture température et humidité (toutes les 2 secondes)
    compteur = compteur + 1
    if compteur >= 4:
        try:
            capteur_dht.measure()
            temp = round(capteur_dht.temperature(), 1)
            hum = round(capteur_dht.humidity(), 1)
        except:
            pass
        compteur = 0
    
    # 3. Déclenchement alarme sonore
    etat = gerer_alarme(ppm)
    
    # 4. Affichage sur écran OLED (Gaz + Temp + Humidité + État)
    afficher_ecran(ppm, temp, hum, etat)
    
    # 5. Télémétrie JSON
    msg = {
        "ppm": ppm,
        "temp": temp,
        "hum": hum,
        "status": etat
    }
    print(json.dumps(msg))
    
    time.sleep(0.5)
