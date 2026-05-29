import { useEffect, useState } from "react";
import api from "./api";

export default function Dashboard() {
  const [invoices, setInvoices] = useState([]);
  const [client, setClient] = useState("");
  const [amount, setAmount] = useState("");

  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);

  // --------------------
  // FETCH INVOICES
  // --------------------
  const fetchInvoices = async () => {
    setLoading(true);

    try {
      const res = await api.get("/invoices");
      setInvoices(res.data);
    } catch (err) {
      console.error("Error fetching invoices", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvoices();
  }, []);

  // --------------------
  // CREATE INVOICE
  // --------------------
  const createInvoice = async () => {
    if (!client || !amount) return;

    setCreating(true);

    try {
      await api.post("/invoices", {
        client,
        amount: Number(amount),
      });

      setClient("");
      setAmount("");
      fetchInvoices();
    } catch (err) {
      alert("Error creating invoice");
    } finally {
      setCreating(false);
    }
  };

  // --------------------
  // DELETE INVOICE
  // --------------------
  const deleteInvoice = async (id) => {
    try {
      await api.delete(`/invoices/${id}`);
      fetchInvoices();
    } catch (err) {
      alert("Error deleting invoice");
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      {/* HEADER */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Invoice Dashboard</h1>
      </div>

      {/* CREATE INVOICE CARD */}
      <div className="bg-white p-6 rounded-2xl shadow mb-6">
        <h2 className="text-xl font-semibold mb-4">Create Invoice</h2>

        <div className="flex gap-3 flex-wrap">
          <input
            className="border p-2 rounded-lg w-full md:w-1/3"
            placeholder="Client"
            value={client}
            onChange={(e) => setClient(e.target.value)}
          />

          <input
            className="border p-2 rounded-lg w-full md:w-1/3"
            placeholder="Amount"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
          />

          <button
            onClick={createInvoice}
            disabled={creating}
            className={`px-4 py-2 rounded-lg text-white ${
              creating
                ? "bg-gray-400 cursor-not-allowed"
                : "bg-blue-600 hover:bg-blue-700"
            }`}
          >
            {creating ? "Creating..." : "Add Invoice"}
          </button>
        </div>
      </div>

      {/* INVOICES TABLE */}
      <div className="bg-white p-6 rounded-2xl shadow">
        <h2 className="text-xl font-semibold mb-4">Your Invoices</h2>

        {/* LOADING */}
        {loading ? (
          <p className="p-4 text-gray-500">Loading invoices...</p>
        ) : invoices.length === 0 ? (
          /* EMPTY STATE */
          <p className="p-4 text-gray-500">
            No invoices yet. Create your first one 👆
          </p>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="text-left border-b">
                <th className="p-2">Client</th>
                <th className="p-2">Amount</th>
                <th className="p-2">Status</th>
                <th className="p-2">Action</th>
              </tr>
            </thead>

            <tbody>
              {invoices.map((inv) => (
                <tr key={inv.id} className="border-b">
                  <td className="p-2">{inv.client}</td>
                  <td className="p-2">${inv.amount}</td>
                  <td className="p-2">
                    <span className="px-2 py-1 bg-yellow-100 text-yellow-700 rounded">
                      {inv.status}
                    </span>
                  </td>
                  <td className="p-2">
                    <button
                      onClick={() => deleteInvoice(inv.id)}
                      className="text-red-600 hover:underline"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}