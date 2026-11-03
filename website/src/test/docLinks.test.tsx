import React from "react";
import { describe, expect, it, vi } from "vitest";
import { renderToString } from "react-dom/server";
import { DocCard } from "@/components/DocCard";
import { FolderView } from "@/components/FolderView";
import { DocsSidebar } from "@/components/DocsSidebar";
import type { Doc } from "@/lib/docs";
import type { Folder } from "@/lib/tree";

vi.mock("next/navigation", () => ({
  useParams: () => ({ slug: [] }),
}));

const mockDoc: Doc = {
  path: "output/Verbali/verbale.pdf",
  rel: "Verbali/verbale.pdf",
  name: "verbale.pdf",
  title: "Verbale Interno",
  categories: ["Verbali"],
  category: "Verbali",
  date: "2026-10-15",
  size: 1024,
};

const mockFolder: Folder = {
  name: "Verbali",
  path: "Verbali",
  folders: [],
  docs: [mockDoc],
};

describe("document link target attributes", () => {
  it("renders DocCard with target='_blank' and rel='noreferrer'", () => {
    const html = renderToString(<DocCard doc={mockDoc} />);
    expect(html).toContain('href="/documenti/Verbali/verbale.pdf"');
    expect(html).toContain('target="_blank"');
    expect(html).toContain('rel="noreferrer"');
  });

  it("renders FolderView document link with target='_blank' and rel='noreferrer'", () => {
    const html = renderToString(<FolderView folder={mockFolder} />);
    expect(html).toContain('href="/documenti/Verbali/verbale.pdf"');
    expect(html).toContain('target="_blank"');
    expect(html).toContain('rel="noreferrer"');
  });

  it("renders DocsSidebar document link with target='_blank' and rel='noreferrer'", () => {
    const html = renderToString(<DocsSidebar tree={mockFolder} docs={[mockDoc]} />);
    expect(html).toContain('href="/documenti/Verbali/verbale.pdf"');
    expect(html).toContain('target="_blank"');
    expect(html).toContain('rel="noreferrer"');
  });
});
