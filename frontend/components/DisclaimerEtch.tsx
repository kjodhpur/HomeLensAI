const TEXT = "System architecture surfaces consumer allegation signals; does not compile verified legal findings.";

/** The allegation disclaimer, etched into the bottom edge of the glass. Two offset layers shift against each other with pointer parallax. */
export function DisclaimerEtch() {
  return (
    <footer className="etch" role="contentinfo">
      <span className="etch-layer back" aria-hidden="true">
        {TEXT}
      </span>
      <span className="etch-layer front">{TEXT}</span>
    </footer>
  );
}
