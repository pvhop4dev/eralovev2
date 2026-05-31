import { describe, it, expect } from "vitest";
import { cn } from "./utils";

describe("cn utility function", () => {
  it("should merge class names correctly", () => {
    expect(cn("px-4", "py-2")).toBe("px-4 py-2");
  });

  it("should handle conditional classes", () => {
    expect(cn("px-4", true && "py-2", false && "bg-red-500")).toBe("px-4 py-2");
  });

  it("should resolve tailwind conflicts", () => {
    expect(cn("px-4 p-6")).toBe("p-6");
  });
});
