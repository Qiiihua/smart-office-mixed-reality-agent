/**
 * lights.js — Simulated WoT Smart Lights (port 3002)
 *
 * Exposes a W3C WoT Thing Description at http://localhost:3002/lights
 *
 * Properties : brightness — current brightness level (0–100)
 *              mode       — current lighting mode string (e.g. "focus-mode")
 * Action     : setLighting — set mode and brightness together
 */

const { Servient } = require("@node-wot/core");
const { HttpServer } = require("@node-wot/binding-http");

const servient = new Servient();
servient.addServer(new HttpServer({ port: 3002 }));

servient.start().then((WoT) => {
  let brightness = 0;
  let mode = "off";

  WoT.produce({
    title: "SmartLights",
    id: "urn:smart-office:lights",
    securityDefinitions: { nosec_sc: { scheme: "nosec" } },
    security: ["nosec_sc"],
    properties: {
      brightness: {
        type: "number",
        readOnly: true,
        description: "Current brightness level (0–100)",
      },
      mode: {
        type: "string",
        readOnly: true,
        description: "Current lighting mode (off | focus-mode | video-call-mode)",
      },
    },
    actions: {
      setLighting: {
        input: {
          type: "object",
          properties: {
            mode:       { type: "string" },
            brightness: { type: "number" },
          },
        },
        description: "Set lighting mode and brightness simultaneously",
      },
    },
    events: {},
  }).then((thing) => {
    thing.setPropertyReadHandler("brightness", () => brightness);
    thing.setPropertyReadHandler("mode",       () => mode);

    thing.setActionHandler("setLighting", async (params) => {
      const input = await params.value();
      if (input.mode       !== undefined) mode       = input.mode;
      if (input.brightness !== undefined) brightness = input.brightness;
      console.log(`[Lights] mode=${mode}  brightness=${brightness}`);
    });

    thing.expose();
    console.log("[Lights] Running on http://localhost:3002/lights");
  });
});
