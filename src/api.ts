import axios from "axios";

let accessToken = "";

export const getToken = async () => {
  const url = import.meta.env.VITE_DB_API_URL;
  const apiKey = import.meta.env.VITE_DB_API_KEY;

  const response = await axios.post(url, {
    key: apiKey,
  });
  accessToken = response.data.access_token;
  //TODO handle errors
};

export const fetchData = async (endpoint: string, data) => {
  const url = `${import.meta.env.VITE_DB_ENDPOINT_URL}/${endpoint}`;

  if (!accessToken) {
    await getToken(); //TODO refresh the token after 24H or so
  }

  try {
    const result = await axios.post(url, data, {
      headers: {
        Accept: "application/json",
        Authorization: `Bearer ${accessToken}`,
      },
    });
    return result.data;
  } catch (err) {
    console.error("Error fetching data:", err);
    return { error: err }; //TODO really use it
  }
};
