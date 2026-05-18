/**
 * thermostat.js — Simulated WoT Thermostat (port 3001)
 *
 * Exposes a W3C WoT Thing Description at http://localhost:3001/thermostat
 *
 * Property : temperature        — current room temperature (read-only)
 * Action   : setTemperature     — set target temperature; reaches it after 3 s
 * Event    : temperatureReached — emitted when current temp equals target
 */

const { Servient } = require("@node-wot/core");
const { HttpServer } = require("@node-wot/binding-http");

const servient = new Servient();
servient.addServer(new HttpServer({ port: 3001 }));

servient.start().then((WoT) => {
  let currentTemp = 28.0;
  let targetTemp = 28.0;

  WoT.produce({
    title: "Thermostat",
    id: "urn:smart-office:thermostat",
    securityDefinitions: { nosec_sc: { scheme: "nosec" } },
    security: ["nosec_sc"],
    properties: {
      temperature: {
        type: "number",
        readOnly: true,
        observable: true,
        description: "Current room temperature in °C",
      },
    },
    actions: {
      setTemperature: {
        input: { type: "number" },
        description: "Set the target temperature in °C",
      },
    },
    events: {
      temperatureReached: {
        data: { type: "number" },
        description: "Emitted when the room reaches the target temperature",
      },
    },
  }).then((thing) => {
    // Return the current temperature when the property is read
    thing.setPropertyReadHandler("temperature", () => currentTemp);

    // When setTemperature is invoked, simulate reaching the target after 3 s
    thing.setActionHandler("setTemperature", async (params) => {
      targetTemp = await params.value();
      console.log(`[Thermostat] Target set to ${targetTemp}°C`);

      setTimeout(() => {
        currentTemp = targetTemp;
        thing.emitEvent("temperatureReached", currentTemp);
        console.log(`[Thermostat] Reached ${currentTemp}°C — event emitted`);
      }, 3000);
    });

    thing.expose();
    console.log("[Thermostat] Running on http://localhost:3001/thermostat");
  });
});
