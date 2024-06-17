interface FootnoteValueType {
  number_relative: number;
  number_abs: number;
  content: {
    text: string;
    style: string;
  }[];
  highlight?: string;
}

interface FootnoteType {
  type: "footnote";
  value: FootnoteValueType;
  highlight?: string;
}

interface StringType {
  type: string;
  value: string;
  highlight?: string;
}

type ContentType = FootnoteType | StringType;
