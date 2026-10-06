// Static data exported from Rithik's artifacts by scripts/export_frontend_data.py (see frontend/data/).
import aspectsJson from "@/data/aspects.json";
import examplesJson from "@/data/examples.json";
import overviewJson from "@/data/overview.json";
import providersJson from "@/data/providers.json";
import type { Aspect, Example, Overview, Provider } from "./types";

export const providers = providersJson as unknown as Provider[];
export const aspects = aspectsJson as unknown as Aspect[];
export const overview = overviewJson as unknown as Overview;
export const examples = examplesJson as unknown as Example[];
