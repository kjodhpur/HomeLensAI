import type { Metadata } from "next";
import { Icon } from "@/components/site/Icon";
import { Card, PageHero, Section } from "@/components/site/ui";
import { SITE } from "@/lib/site";

export const metadata: Metadata = {
  title: "Contact",
  description: "Get in touch with the HomeLens AI team about feedback, pilots or responsible-use questions.",
};

export default function ContactPage() {
  const { contactEmail, repoUrl } = SITE;
  const mail = (subject: string) => (contactEmail ? `mailto:${contactEmail}?subject=${encodeURIComponent(subject)}` : null);
  const cards = [
    { icon: "mail", title: "Feedback and questions", body: "Tell us what worked, what confused you and what you would want next.", subject: "HomeLens AI feedback" },
    { icon: "users", title: "Pilot interest", body: "Interested in trying HomeLens on your own review export? Describe your team and volume.", subject: "HomeLens AI pilot interest" },
    { icon: "shield", title: "Responsible-use concerns", body: "Think a signal is wrong, unfair or misleading? Please tell us. Do not include personal data.", subject: "HomeLens AI responsible-use concern" },
  ] as const;
  return (
    <>
      <PageHero eyebrow="Contact" title="Talk to the team." lead="HomeLens AI is a student project, so replies may take a few days." />
      <Section tight>
        <div className="grid c3">
          {cards.map((c) => {
            const href = mail(c.subject);
            return (
              <Card key={c.title} icon={c.icon} title={c.title}>
                <p>{c.body}</p>
                {href ? (
                  <a className="btn ghost sm" style={{ marginTop: 14, alignSelf: "flex-start" }} href={href}>
                    Email us
                  </a>
                ) : null}
              </Card>
            );
          })}
        </div>
        {!contactEmail && (
          <div className="notice glass" style={{ marginTop: 24 }}>
            <Icon name="mail" size={20} />
            <p>A public contact address has not been published yet. Reach the team through your CIS 509 course channel{repoUrl ? <> or <a href={repoUrl}>the project repository</a></> : null}.</p>
          </div>
        )}
        {repoUrl && (
          <p className="foot-note">
            Found a bug? <a href={`${repoUrl}/issues`} style={{ color: "var(--accent-ink)" }}>Open an issue</a>.
          </p>
        )}
      </Section>
    </>
  );
}
