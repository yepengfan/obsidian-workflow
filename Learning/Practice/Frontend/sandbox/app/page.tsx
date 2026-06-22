import Link from "next/link";
import { readdirSync, statSync } from "fs";
import { join } from "path";

function getChallenges(): string[] {
  const dir = join(process.cwd(), "app/challenges");
  try {
    return readdirSync(dir).filter((name) =>
      statSync(join(dir, name)).isDirectory()
    );
  } catch {
    return [];
  }
}

export default function Home() {
  const challenges = getChallenges();

  return (
    <main className="mx-auto max-w-2xl px-6 py-12">
      <h1 className="mb-2 text-3xl font-bold">Frontend Practice</h1>
      <p className="mb-8 text-gray-500">
        React &amp; Next.js challenges from GreatFrontEnd
      </p>

      {challenges.length === 0 ? (
        <p className="text-gray-400">
          No challenges yet. Run{" "}
          <code className="rounded bg-gray-200 px-1.5 py-0.5 text-sm">
            /frontend/solve Accordion
          </code>{" "}
          to get started.
        </p>
      ) : (
        <ul className="space-y-2">
          {challenges.map((name) => (
            <li key={name}>
              <Link
                href={`/challenges/${name}`}
                className="block rounded-lg border border-gray-200 px-4 py-3 transition-colors hover:border-blue-400 hover:bg-blue-50"
              >
                {name}
              </Link>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
