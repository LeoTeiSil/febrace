import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import DashboardNavbar from "../components/DashboardNavbar";
import "../styles/informacoes.css";

interface Doenca {
  descricao: string;
  sintomas: string[];
  tratamentos: string[];
  aviso: string;
}

const Informacoes: React.FC = () => {

  const { doenca } = useParams<{ doenca: string }>();
  const navigate = useNavigate();

  const [dados, setDados] = useState<Doenca | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {

    if (!doenca) return;

    const buscarDoenca = async () => {

      try {

        const response = await fetch(
          `http://127.0.0.1:8000/doenca/${doenca}`
        );

        if (!response.ok) {
          console.error("Erro na resposta:", response.status);
          setLoading(false);
          return;
        }

        const data = await response.json();

        setDados(data);

      } catch (error) {

        console.error("Erro ao buscar doença:", error);

      } finally {

        setLoading(false);

      }

    };

    buscarDoenca();

  }, [doenca]);

  if (loading) {

    return (
      <div className="info-layout">
        <DashboardNavbar />
        <p style={{ padding: "40px" }}>Carregando informações...</p>
      </div>
    );

  }

  if (!dados) {

    return (
      <div className="info-layout">
        <DashboardNavbar />
        <p style={{ padding: "40px" }}>Doença não encontrada.</p>
      </div>
    );

  }

  return (

    <div className="info-layout">

      <div className="info-content">

        <DashboardNavbar />

        <div className="info-container">

          <button className="voltar-btn" onClick={() => navigate(-1)}>
            <ArrowLeft size={20} />
          </button>

          <h1 className="info-title">{doenca}</h1>

          <p className="info-descricao">
            {dados.descricao}
          </p>

          <h2 className="secao-titulo">Sintomas</h2>

          <ul className="lista">

            {dados.sintomas && dados.sintomas.length > 0 ? (
              dados.sintomas.map((item, index) => (
                <li key={index}>{item}</li>
              ))
            ) : (
              <li>Sintomas não disponíveis</li>
            )}

          </ul>

          <h2 className="secao-titulo">Tratamentos</h2>

          <ul className="tratamentos-grid">

            {dados.tratamentos && dados.tratamentos.length > 0 ? (
              dados.tratamentos.map((item, index) => (
                <li key={index}>{item}</li>
              ))
            ) : (
              <li>Tratamentos não disponíveis</li>
            )}

          </ul>

          {dados.aviso && (
            <>
              <h2 className="secao-titulo">Aviso</h2>
              <p>{dados.aviso}</p>
            </>
          )}

        </div>

      </div>

    </div>

  );

};

export default Informacoes;