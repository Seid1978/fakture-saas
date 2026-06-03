import api from "../api";

export const getInvoices = async () => {
  const res = await api.get("/invoices");
  return res.data;
};

export const deleteInvoice = async (id) => {
  const res = await api.delete(`/invoices/${id}`);
  return res.data;
};

export const createInvoice = async (data) => {
  const res = await api.post("/invoices", data);
  return res.data;
};