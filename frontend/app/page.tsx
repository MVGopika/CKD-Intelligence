export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-neutral-950 to-black text-white">
      {/* HERO SECTION */}
      <section className="relative overflow-hidden py-28 px-6 text-center">
        <div className="absolute -top-40 left-1/2 -translate-x-1/2 h-[500px] w-[500px] rounded-full bg-blue-600/20 blur-3xl" />

        <h1 className="relative text-5xl md:text-6xl font-extrabold mb-6 tracking-tight">
          CKD Intelligence
        </h1>

        <p className="relative max-w-2xl mx-auto text-lg md:text-xl text-zinc-400 mb-10">
          AI-powered clinical decision support system designed to assist
          healthcare professionals in detecting, monitoring, and managing
          Chronic Kidney Disease with precision.
        </p>

        <div className="relative flex justify-center gap-6">
          <a
            href="/auth/login"
            className="rounded-xl bg-blue-600 px-8 py-3 font-semibold hover:bg-blue-700 transition-all shadow-lg shadow-blue-600/30"
          >
            Log In
          </a>

          <a
            href="/auth/register"
            className="rounded-xl bg-green-600 px-8 py-3 font-semibold hover:bg-green-700 transition-all shadow-lg shadow-green-600/30"
          >
            Get Started
          </a>
        </div>
      </section>

      {/* FEATURES SECTION */}
      <section className="px-6 pb-24 max-w-6xl mx-auto">
        <h2 className="text-3xl font-bold text-center mb-14">
          Why CKD Intelligence?
        </h2>

        <div className="grid md:grid-cols-3 gap-8">
          <div className="rounded-2xl border border-zinc-800 bg-neutral-900 p-8 hover:border-blue-500 transition-all">
            <h3 className="text-xl font-semibold mb-4">
              🧠 AI Risk Prediction
            </h3>
            <p className="text-zinc-400">
              Machine learning models analyze patient lab data to predict CKD
              progression and risk stages with high accuracy.
            </p>
          </div>

          <div className="rounded-2xl border border-zinc-800 bg-neutral-900 p-8 hover:border-green-500 transition-all">
            <h3 className="text-xl font-semibold mb-4">📊 Clinical Insights</h3>
            <p className="text-zinc-400">
              Converts raw medical inputs into structured insights including
              staging, recommendations, and monitoring guidance.
            </p>
          </div>

          <div className="rounded-2xl border border-zinc-800 bg-neutral-900 p-8 hover:border-purple-500 transition-all">
            <h3 className="text-xl font-semibold mb-4">
              🔐 Secure Architecture
            </h3>
            <p className="text-zinc-400">
              Built with authentication, encrypted storage, and secure API
              infrastructure to ensure patient data protection.
            </p>
          </div>
        </div>
      </section>

      {/* CALL TO ACTION */}
      <section className="bg-gradient-to-r from-blue-900/30 to-green-900/30 py-20 text-center">
        <h2 className="text-3xl font-bold mb-6">
          Ready to Transform CKD Management?
        </h2>

        <p className="text-zinc-400 mb-8 max-w-xl mx-auto">
          Join the next generation of AI-powered healthcare systems and bring
          smarter decision-making to clinical practice.
        </p>

        <a
          href="/auth/register"
          className="rounded-xl bg-white text-black px-8 py-3 font-semibold hover:opacity-90 transition"
        >
          Create Your Account
        </a>
      </section>
    </div>
  );
}
