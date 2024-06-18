export const ContentText: React.FC<{
  className: string;
  value: string;
  highlight: string | undefined;
}> = ({ value, className, highlight }) => {
  if (highlight) {
    const wordsToHighlight = highlight.split(/\s+/).filter((word) => word);

    if (wordsToHighlight.length > 0) {
      const regex = new RegExp(`(${wordsToHighlight.join("|")})`, "gi");
      const parts = value.split(regex);

      return (
        <span className={className}>
          {parts.map((part, index) =>
            wordsToHighlight.some(
              (word) => word.toLowerCase() === part.toLowerCase(),
            ) ? (
              <span key={index} className="highlight">
                {part}
              </span>
            ) : (
              <span key={index}>{part}</span>
            ),
          )}
        </span>
      );
    }
  }

  return <span className={className}>{value}</span>;
};
