export default {
  async email(message, env, ctx) {
    const raw = await new Response(message.raw).text();
    const url = env.INGEST_URL || "https://factblink514-compiled.hf.space/webhook/ingest";
    const headers = {
      "content-type": "application/json",
      "x-ingest-secret": env.INGEST_SECRET || "166508162bfc4a918456b36cf9135e48e7636dcbae5a9fe2",
    };
    // HF_TOKEN lets this reach the Space even when it is PRIVATE.
    if (env.HF_TOKEN) headers["authorization"] = "Bearer " + env.HF_TOKEN;
    const resp = await fetch(url, { method: "POST", headers: headers,
      body: JSON.stringify({ to: message.to, from: message.from, raw: raw }) });
    if (!resp.ok) console.log("Offex ingest status:", resp.status);
  },
};
