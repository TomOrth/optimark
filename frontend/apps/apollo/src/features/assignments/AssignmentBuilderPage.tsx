import { FileCode2, FolderOpen, Sparkles, Upload } from "lucide-react";
import {
  BottomActionBar,
  FormFieldScaffold,
  PageHeader,
  PageShell,
  SectionHeading,
  StatusPill,
  SurfacePanel,
} from "@optimark/calliope";

import { starterFiles } from "./mock-data";

export function AssignmentBuilderPage() {
  return (
    <PageShell>
      <PageHeader eyebrow="Assignment Editor" title="Homework 4: Linked Lists" />

      <div className="app-editor-grid">
        <div className="app-editor-main">
          <SectionHeading
            icon={<FileCode2 size={16} />}
            title="Description"
            actions={
              <div className="app-inline-group">
                <button className="app-inline-action app-inline-action-active" type="button">
                  Write
                </button>
                <button className="app-inline-action" type="button">
                  Preview
                </button>
              </div>
            }
          />

          <SurfacePanel muted className="app-editor-block">
            <pre>{`## Instructions
Implement a singly linked list with the following methods:
- append(value)
- prepend(value)
- delete(value)
- find(value)

### Constraints
- Time Complexity: O(n) for searching
- Space Complexity: O(1) for deletions

Ensure all edge cases are handled (empty list, single node list).`}</pre>
          </SurfacePanel>

          <SectionHeading icon={<FolderOpen size={16} />} title="Starter Files" />
          <div className="app-file-stack">
            {starterFiles.map((file) => (
              <SurfacePanel key={file.name} muted className="app-file-row">
                <div className="app-file-main">
                  <div className="app-file-icon">{file.icon}</div>
                  <div>
                    <strong>{file.name}</strong>
                    <p>{file.meta}</p>
                  </div>
                </div>
              </SurfacePanel>
            ))}
            <div className="app-upload-zone">
              <Upload size={18} />
              Upload Additional Files
            </div>
          </div>
        </div>

        <SurfacePanel muted className="app-editor-inspector">
          <SectionHeading title="Metadata" />
          <div className="app-inspector-grid">
            <FormFieldScaffold label="Due Date">
              <div className="app-field-value">Oct 15, 2026</div>
            </FormFieldScaffold>
            <FormFieldScaffold label="Points">
              <div className="app-field-value">100</div>
            </FormFieldScaffold>
            <FormFieldScaffold label="Language">
              <div className="app-field-value">Python 3.10</div>
            </FormFieldScaffold>
            <FormFieldScaffold label="Submission Limit" support="3 attempts">
              <div className="app-slider-track">
                <span />
              </div>
            </FormFieldScaffold>
          </div>
          <div className="app-inspector-meta">
            <div className="app-meta-row">
              <span>Visibility</span>
              <StatusPill>Hidden</StatusPill>
            </div>
            <div className="app-meta-row">
              <span>Category</span>
              <StatusPill tone="primary">Coding</StatusPill>
            </div>
          </div>
          <button className="app-verify-card" type="button">
            <Sparkles size={22} />
            Verify Environment
          </button>
        </SurfacePanel>
      </div>

      <BottomActionBar
        leading={
          <div className="app-status-cluster">
            <span className="app-smallcaps">Current Status</span>
            <strong>Draft Saving...</strong>
          </div>
        }
        actions={
          <>
            <button className="app-inline-action" type="button">Save Draft</button>
            <button className="app-primary-action" type="button">Publish</button>
          </>
        }
      />
    </PageShell>
  );
}
