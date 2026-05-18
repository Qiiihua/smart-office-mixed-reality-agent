/**
 * ventilation.js — Simulated WoT Ventilation System (port 3004)
 *
 * Exposes a W3C WoT Thing Description at http://localhost:3004/ventilation
 *
 * Property : active          — whether ventilation is currently running (bool)
 * Action   : setVentilation  — turn ventilation on (true) or off (false)
 *
 * Typically activated by the Reflex Loop in response to co2ExceededThreshold.
 */

const { Servient } = require("@node-wot/core");
const { HttpServer } = require("@node-wot/binding-http");

const servient = new Servient();
servient.addServer(new HttpServer({ port: 3004 }));

servient.start().then((WoT) => {
  let active = false;

  WoT.produce({
    title: "Ventilation",
    id: "urn:smart-office:ventilation",
    securityDefinitions: { nosec_sc: { scheme: "nosec" } },
    security: ["nosec_sc"],
    properties: {
      active: {
        type: "boolean",
        readOnly: true,
        description: "True if ventilation is currently running",
      },
    },
    actions: {
      setVentilation: {
        input: { type: "boolean" },
        description: "Turn ventilation on (true) or off (false)",
      },
    },
    events: {},
  }).then((thing) => {
    thing.setPropertyReadHandler("active", () => active);

    thing.setActionHandler("setVentilation", async (params) => {
      active = await params.value();
      console.log(`[Ventilation] active=${active}`);
    });

    thing.expose();
    console.log("[Ventilation] Running on http://localhost:3004/ventilation");
  });
});
