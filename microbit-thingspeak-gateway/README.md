# Connector Micro:bit → ThingSpeak

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

**5.1.2** — actualització de crèdits, propietats i llicència, sense canvis de funcionament.

## Codi font i llicència

El **connector** es distribueix sota la **Llicència Pública de la Unió Europea (EUPL), versió 1.2**.

- Text íntegre: [LICENSE.txt](LICENSE.txt)
- Text oficial de l'EUPL 1.2: https://interoperable-europe.ec.europa.eu/sites/default/files/inline-files/EUPL%20v1_2%20ES.txt
- Codi font del connector: https://github.com/edutechlabsis-bot/edutechlabs-assets/tree/main/microbit-thingspeak-gateway

Els **materials educatius** d'Estació Meteorològica en Xarxa es regeixen, per separat, per **CC BY-NC-SA 4.0**. Aquesta llicència de materials no s'aplica al codi del connector.
