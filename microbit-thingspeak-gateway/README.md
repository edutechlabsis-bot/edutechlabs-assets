# Connector Micro:bit → ThingSpeak

Connector per a Windows que permet enviar a **ThingSpeak** les dades generades per una **micro:bit** connectada per USB/Serial.

Aquest connector s'ha desenvolupat dins del projecte **Estació Meteorològica en Xarxa**.

## Crèdits

**Projecte:** Estació Meteorològica en Xarxa  
**Projecte original:** Anton Nin Nin i Paula Pacho Ruiz  
**Connector Micro:bit → ThingSpeak desenvolupat per:** Ignasi Sánchez Rodríguez  
**Marc:** Mentoria Digital 4.0 · 2026

Web del projecte: https://linktr.ee/meteorologiaenxarxa

## Funcionament

```
micro:bit → USB / Serial → Connector Windows → Internet → ThingSpeak
```

La micro:bit envia dades pel port sèrie i el connector les rep i les publica automàticament al canal de ThingSpeak mitjançant la **Write API Key**.

El connector:

- detecta automàticament la micro:bit connectada;
- permet configurar i canviar la Write API Key;
- envia fins a 8 valors als camps `field1`–`field8`;
- respecta un interval mínim d'enviament de 15 segons;
- inclou una finestra de diagnosi amb el port sèrie, l'última dada rebuda, l'`entry_id` i la resposta de ThingSpeak;
- inclou l'apartat **«Quant a»** amb els crèdits del projecte, l'autoria del connector i la llicència.

## Versió

Versió actual: **5.1.1**

## Llicència del connector

Aquest programari es distribueix sota la **PolyForm Noncommercial License 1.0.0**:

https://polyformproject.org/licenses/noncommercial/1.0.0/

La redistribució del connector ha de conservar l'avís de llicència i l'enllaç corresponent.

> La llicència anterior correspon al connector Micro:bit → ThingSpeak. Els materials originals del projecte Estació Meteorològica en Xarxa mantenen els crèdits i la llicència indicats pels seus autors.

## Projecte original

Recursos originals vinculats a l'Estació Meteorològica en Xarxa:

- Paula Pacho Ruiz: https://github.com/Paula-Pacho/micro-bit/tree/e92696bad1bd214e4ae19149dc8984d2f9ed5a35/Projectes%20/%20IoT-Estacio-Meteo
- Anton Nin Nin: https://github.com/antonnin/estacions-meteo-escoles/
