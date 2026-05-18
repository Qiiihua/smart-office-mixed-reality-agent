/**
 * co2_sensor.js — Simulated WoT CO₂ Sensor (port 3003)
 *
 * Exposes a W3C WoT Thing Description at http://localhost:3003/co2sensor
 *
 * Property : co2_ppm               — current CO₂ concentration (ppm)
 * Action   : simulateSpike         — manually set co2_ppm to any value
 * Event    : co2ExceededThreshold  — emitted when co2_ppm > 1000 ppm
 *
 * The simulateSpike action lets integration tests trigger the event
 * without needing real air-quality hardware.
 */

const { Servient } = require("@node-wot/core");
const { HttpServer } = require("@node-wot/binding-http");

const servient = new Servient();
servient.addServer(new HttpServer({ port: 3003 }));

const CO2_THRESHOLD = 1000; // ppm — matches config.CO2_THRESHOLD_PPM in Python

servient.start().then((WoT) => {
  let co2_ppm = 420; // typical outdoor/normal indoor baseline

  WoT.produce({
    title: "CO2Sensor",
    id: "urn:smart-office:co2sensor",
    securityDefinitions: { nosec_sc: { scheme: "nosec" } },
    security: ["nosec_sc"],
    properties: {
      co2_ppm: {
        type: "number",
        readOnly: true,
        observable: true,
        description: "Current CO₂ concentration in parts per million",
      },
    },
    actions: {
      simulateSpike: {
        input: { type: "number" },
        description: `Set co2_ppm to any value; emits co2ExceededThreshold if > ${CO2_THRESHOLD}`,
      },
    },
    events: {
      co2ExceededThreshold: {
        data: { type: "number" },
        description: `Emitted when CO₂ exceeds ${CO2_THRESHOLD} ppm`,
      },
    },
  }).then((thing) => {
    thing.setPropertyReadHandler("co2_ppm", () => co2_ppm);

    thing.setActionHandler("simulateSpike", async (params) => {
      co2_ppm = await params.value();
      console.log(`[CO2Sensor] Level set to ${co2_ppm} ppm`);

      if (co2_ppm > CO2_THRESHOLD) {
        thing.emitEvent("co2ExceededThreshold", co2_ppm);
        console.log(`[CO2Sensor] Threshold exceeded — event emitted`);
      }
    });

    thing.expose();
    console.log("[CO2Sensor] Running on http://localhost:3003/co2sensor");
  });
});
