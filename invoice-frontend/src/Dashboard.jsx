import { useEffect, useState } from "react";
import { getInvoices, deleteInvoice } from "./services/invoices";

export default function Dashboard() {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadInvoices();
  }, []);

  async function loadInvoices() {
    try {
      setLoading(true);
      const data = await getInvoices();
      setInvoices(data || []);
    } catch (err) {
      console.error(err);
      setError("Failed to load invoices");
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id) {
    const previous = invoices;

    // optimistic update
    setInvoices((prev) => prev.filter((inv) => inv.id !== id));

    try {
      await deleteInvoice(id);
    } catch (err) {
      console.error("Delete failed:", err);
      setInvoices(previous); // rollback
    }
  }

  const totalAmount = invoices.reduce(
    (sum, i) => sum + Number(i.amount || 0),
    0
  );

  const pendingCount = invoices.filter(
    (i) => i.status === "Pending"
  ).length;

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-black mx-auto mb-3"></div>
          <p className="text-gray-500">Loading invoices...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-screen flex items-center justify-center">
        <p className="text-red-500">{error}</p>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-100">

      {/* SIDEBAR */}
      <aside className="w-64 bg-white shadow-md p-5">
        <h1 className="text-xl font-bold mb-8">Invoice SaaS</h1>

        <nav className="space-y-4">
          <button className="w-full text-left font-medium text-gray-700 hover:text-black">
            📄 Fakture
          </button>
          <button className="w-full text-left text-gray-600 hover:text-black">
            👤 Klijenti
          </button>
          <button className="w-full text-left text-gray-600 hover:text-black">
            ⚙️ Settings
          </button>
        </nav>
      </aside>

      {/* MAIN */}
      <main className="flex-1 p-6">

        {/* HEADER */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-semibold">Dashboard</h2>

          <button
            className="bg-black text-white px-4 py-2 rounded-lg hover:bg-gray-800"
            onClick={() => alert("Next: Create Invoice Modal")}
          >
            + Nova faktura
          </button>
        </div>

        {/* STATS */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-white p-4 rounded-xl shadow">
            <p className="text-gray-500">Ukupno faktura</p>
            <h3 className="text-xl font-bold">{invoices.length}</h3>
          </div>

          <div className="bg-white p-4 rounded-xl shadow">
            <p className="text-gray-500">Ukupno prihoda</p>
            <h3 className="text-xl font-bold">
              {totalAmount.toLocaleString()} KM
            </h3>
          </div>

          <div className="bg-white p-4 rounded-xl shadow">
            <p className="text-gray-500">Pending</p>
            <h3 className="text-xl font-bold">{pendingCount}</h3>
          </div>
        </div>

        {/* TABLE */}
        <div className="bg-white rounded-xl shadow overflow-hidden">

          {invoices.length === 0 ? (
            <div className="p-10 text-center text-gray-500">
              Nema faktura 📭
            </div>
          ) : (
            <table className="w-full">
              <thead className="bg-gray-50 text-left">
                <tr>
                  <th className="p-3">Klijent</th>
                  <th className="p-3">Iznos</th>
                  <th className="p-3">Status</th>
                  <th className="p-3">Datum</th>
                  <th className="p-3">Akcija</th>
                </tr>
              </thead>

              <tbody>
                {invoices.map((inv) => (
                  <tr key={inv.id} className="border-t hover:bg-gray-50">

                    <td className="p-3 font-medium">
                      {inv.client}
                    </td>

                    <td className="p-3">
                      {Number(inv.amount || 0).toLocaleString()} KM
                    </td>

                    <td className="p-3">
                      <span
                        className={`px-2 py-1 rounded text-sm ${
                          inv.status === "Paid"
                            ? "bg-green-100 text-green-700"
                            : "bg-yellow-100 text-yellow-700"
                        }`}
                      >
                        {inv.status}
                      </span>
                    </td>

                    <td className="p-3 text-gray-600">
                      {inv.date
                        ? new Date(inv.date).toLocaleDateString("en-GB")
                        : "-"}
                    </td>

                    <td className="p-3">
                      <button
                        onClick={() => handleDelete(inv.id)}
                        className="text-red-500 hover:text-red-700"
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

      </main>
    </div>
  );
}