# Connector Microbit-ThingSpeak-Serial

Aplicació per a Windows que envia a **ThingSpeak** les dades generades per una **micro:bit** connectada per USB/Serial.

## Identificació

- **Projecte:** Estació Meteorològica en Xarxa
- **Desenvolupador del connector:** Ignasi Sánchez Rodríguez
- **Programa:** Mentoria 4.0
- **Copyright:** © 2026 Generalitat de Catalunya · Departament d'Educació i Formació Professional
- **Llicència del programari:** EUPL 1.2
- **Materials educatius del projecte:** CC BY-NC-SA 4.0 (llicència independent de la del connector)

Web del projecte: https://linktr.ee/meteorologiaenxarxa

## Funcionament

```text
micro:bit → USB / Serial → Connector Windows → Internet → ThingSpeak
```

La micro:bit envia dades pel port sèrie. El connector les rep i les publica automàticament al canal de ThingSpeak mitjançant la seva **Write API Key**.

El connector:

- detecta automàticament la micro:bit connectada;
- permet configurar i canviar la Write API Key;
- envia fins a 8 valors als camps `field1`–`field8`;
- respecta un interval mínim d'enviament de 15 segons;
- ofereix diagnosi amb el port sèrie, l'última dada rebuda, l'`entry_id` i la resposta de ThingSpeak;
- inclou una finestra «Quant a» amb identificació, autoria i llicències.

## Versió

**5.1.4** — actualització menor del nom del connector i del fitxer EXE per comprovar que la Write API Key es conserva després d'una actualització i d'un canvi de carpeta. Sense canvis al sistema de configuració.

**5.1.3** — la configuració de ThingSpeak es conserva entre actualitzacions (AppData), amb migració de versions anteriors i mode portable opcional.

## Codi font i llicència

El **connector** es distribueix sota la **Llicència Pública de la Unió Europea (EUPL), versió 1.2**.

- Text íntegre: [LICENSE.txt](LICENSE.txt)
- Text oficial de l'EUPL 1.2: https://interoperable-europe.ec.europa.eu/sites/default/files/inline-files/EUPL%20v1_2%20ES.txt
- Codi font del connector: https://github.com/edutechlabsis-bot/edutechlabs-assets/tree/main/microbit-thingspeak-gateway

Els **materials educatius** d'Estació Meteorològica en Xarxa es regeixen, per separat, per **CC BY-NC-SA 4.0**. Aquesta llicència de materials no s'aplica al codi del connector.

## Configuració persistent i ús als centres

La primera vegada, introduïu la **Write API Key** del canal ThingSpeak. A partir d'aquell moment, el connector la desa al perfil de Windows, sense necessitat d'administrador:

`%APPDATA%\\Microbit-ThingSpeak-Gateway\\config.json`

Això permet copiar una versió nova de l'EXE, fins i tot a una carpeta diferent, sense tornar a introduir la clau. La configuració és **per usuari Windows**, no global per ordinador. Si hi ha diferents comptes d'usuari, cadascun té la seva configuració.

**Migració de versions anteriors:** executeu una vegada la versió 5.1.3 a la mateixa carpeta de la versió antiga, al costat del fitxer `microbit_thingspeak_config.json`; així en recupera la clau i la desa a AppData. El fitxer antic no s'elimina. Després ja podreu moure les versions noves lliurement.

**Mode portable opcional:** si voleu transportar també la configuració entre ordinadors, creeu manualment un fitxer `microbit_thingspeak_portable.json` al costat de l'EXE amb el contingut del vostre fitxer `config.json`. El connector el prioritzarà i hi desarà els canvis. **Aquest fitxer conté la Write API Key; no el compartiu públicament ni el pengeu a GitHub.**

Per distribuir el connector a diversos ordinadors dels centres només cal copiar l'EXE. Cada perfil d'usuari introdueix la clau una única vegada.
