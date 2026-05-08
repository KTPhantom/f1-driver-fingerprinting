import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[--color-bg] p-6">
      <div className="text-center max-w-md">
        <div className="text-8xl font-black bg-gradient-to-r from-[#E8002D] to-[#FF8000] bg-clip-text text-transparent font-[family-name:var(--font-geist-mono)] mb-4">
          404
        </div>
        <h1 className="text-2xl font-bold mb-2">Off Track</h1>
        <p className="text-sm text-[--color-text-secondary] mb-8">
          Looks like you've run wide. This page doesn't exist on the circuit.
        </p>
        <Link href="/dashboard"
          className="px-6 py-3 rounded-xl font-semibold text-sm bg-gradient-to-r from-[#00D4FF] to-[#7B61FF] text-white hover:opacity-90 transition-opacity">
          Back to Pit Lane
        </Link>
      </div>
    </div>
  );
}
