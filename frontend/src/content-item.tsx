const types = new Set(); //TODO remove

export const ContentItem: React.FC<{ type: string; value: string }> = ({
  type,
  value,
}) => {
  if (!types.has(type)) {
    console.log("TYPE: ", type);
    types.add(type);
  }
  switch (type) {
    case "new_line":
      return value === "\n" ? <br /> : <p />;
    case "heading_title":
      return <h1 className={type}>{value}</h1>;
    case "heading_section":
      return <h2 className={type}>{value}</h2>;
    case "heading_sub-section-bigger":
    case "section_title_secondary":
      return <h3 className={type}>{value}</h3>;
    case "heading_sub-section":
      return <h4 className={type}>{value}</h4>;
    case "heading_letter":
      return <h5 className={type}>{value}</h5>;

    default:
      return <span className={type}>{value}</span>;

    //TODO use, or del
    //   // eslint-disable-next-line no-case-declarations
    //   const [typeKind, typeOrigin] = type.split("_");
    //   // setKind(typeKind);
    //   // setOrigin(typeOrigin);
    //
  }
};
