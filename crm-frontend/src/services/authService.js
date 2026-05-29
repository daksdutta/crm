import API from "./api";

export const loginUser = async (data) => {
  const response = await API.post("api/auth/login", data);
  return response.data;
};