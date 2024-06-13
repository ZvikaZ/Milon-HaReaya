interface FootnoteValueType {
  number_relative: number;
  number_abs: number;
  content: {
    text: string;
    style: string;
  }[];
}

interface FootnoteType {
  type: "footnote";
  value: FootnoteValueType;
}

interface StringType {
  type: string;
  value: string;
}

type ContentType = FootnoteType | StringType;
