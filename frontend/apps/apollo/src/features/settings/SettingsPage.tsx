import { Gauge, Sparkles } from "lucide-react";
import {
  FormFieldScaffold,
  PageHeader,
  PageShell,
  SectionHeading,
  SurfacePanel,
} from "@optimark/calliope";

export function SettingsPage() {
  return (
    <PageShell>
      <PageHeader
        title="Course settings"
        subtitle="Configuration pages can reuse the same inspector and form-field scaffolds from the assignment editor."
      />
      <div className="app-settings-grid">
        <SurfacePanel muted className="app-settings-panel">
          <SectionHeading title="Grading policy" icon={<Gauge size={16} />} />
          <FormFieldScaffold label="Release cadence">
            <div className="app-field-value">Manual review gate</div>
          </FormFieldScaffold>
          <FormFieldScaffold label="Visibility default">
            <div className="app-field-value">Hidden until publish</div>
          </FormFieldScaffold>
        </SurfacePanel>
        <SurfacePanel muted className="app-settings-panel">
          <SectionHeading title="Operational defaults" icon={<Sparkles size={16} />} />
          <FormFieldScaffold label="Autograde retries">
            <div className="app-field-value">2 retries</div>
          </FormFieldScaffold>
          <FormFieldScaffold label="Audit retention">
            <div className="app-field-value">Full term archive</div>
          </FormFieldScaffold>
        </SurfacePanel>
      </div>
    </PageShell>
  );
}
