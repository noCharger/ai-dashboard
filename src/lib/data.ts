import fs from "fs";
import path from "path";
import { DashboardData } from "./types";

export function getDashboardData(): DashboardData {
  const filePath = path.join(process.cwd(), "data", "dashboard.json");
  const raw = fs.readFileSync(filePath, "utf-8");
  return JSON.parse(raw) as DashboardData;
}
