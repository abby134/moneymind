import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-emerald-50 to-teal-50">
      <div className="max-w-4xl mx-auto px-6 py-24 text-center">
        <div className="mb-6 inline-flex items-center gap-2 bg-emerald-100 text-emerald-800 px-4 py-2 rounded-full text-sm font-medium">
          AI-powered · Remembers your patterns · No bank login required
        </div>

        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          The finance coach that <br />
          <span className="text-emerald-600">remembers everything</span>
        </h1>

        <p className="text-xl text-gray-600 mb-12 max-w-2xl mx-auto">
          Upload your bank CSV once a month. MoneyMind analyzes your spending across years,
          finds patterns you never noticed, and tells you why — not just what.
        </p>

        <div className="flex gap-4 justify-center mb-16">
          <Link
            href="/register"
            className="bg-emerald-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:bg-emerald-700 transition"
          >
            Get started free
          </Link>
          <Link
            href="/login"
            className="border border-gray-300 text-gray-700 px-8 py-4 rounded-xl font-semibold text-lg hover:bg-gray-50 transition"
          >
            Sign in
          </Link>
        </div>

        <div className="grid grid-cols-3 gap-8 text-left">
          {[
            {
              icon: "🧠",
              title: "Long-term memory",
              desc: "Remembers 3 years of patterns, not just this month",
            },
            {
              icon: "🔍",
              title: "Behavioral insights",
              desc: "Finds why you overspend, not just that you did",
            },
            {
              icon: "🔒",
              title: "No bank login",
              desc: "Just upload a CSV. Your credentials stay with you",
            },
          ].map((f) => (
            <div key={f.title} className="bg-white rounded-2xl p-6 shadow-sm">
              <div className="text-3xl mb-3">{f.icon}</div>
              <h3 className="font-semibold text-gray-900 mb-2">{f.title}</h3>
              <p className="text-gray-600 text-sm">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
