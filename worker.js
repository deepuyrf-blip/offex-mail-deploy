export default {
  async email(message, env, ctx) {
    const raw = await new Response(message.raw).text();
    const url = env.INGEST_URL || "https://factblink514-compiled.hf.space/webhook/ingest";
    const secret = env.INGEST_SECRET || "166508162bfc4a918456b36cf9135e48e7636dcbae5a9fe2";
    const resp = await fetch(url, {
      method: "POST",
      headers: { "content-type": "application/json", "x-ingest-secret": secret },
      body: JSON.stringify({ to: message.to, from: message.from, raw: raw }),
    });
    if (!resp.ok) console.log("Offex ingest status:", resp.status);
  },
};
