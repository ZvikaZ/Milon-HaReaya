export const ContentText: React.FC<{
  className: string;
  value: string;
  highlight: string | undefined;
}> = ({ value, className, highlight }) => {
  if (highlight && value.includes(highlight)) {
    const parts = value.split(new RegExp(`(${highlight})`, "gi"));

    return (
      <span className={className}>
        {parts.map((part, index) =>
          part === highlight ? (
            <span key={index} className="highlight">
              {part}
            </span>
          ) : (
            <span key={index}>{part}</span>
          ),
        )}
      </span>
    );
  } else {
    return <span className={className}>{value as string}</span>;
  }
};
