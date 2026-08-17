"use client";

import Image from "next/image";
import dynamic from "next/dynamic";
import { FormEvent, useEffect, useRef, useState } from "react";

const CapViewer = dynamic(() => import("@/components/CapViewer"), { ssr: false });

const variants = [
  { name: "OBSIDIAN", detail: "Negro profundo", className: "obsidian", image: "/caps/obsidian.png" },
  { name: "HALO", detail: "Hueso cálido", className: "halo", image: "/caps/halo.png" },
  { name: "COVENANT", detail: "Vino oscuro", className: "covenant", image: "/caps/covenant.png" },
];

const turntable = [
  { name: "FRENTE", image: "/caps/obsidian.png" },
  { name: "PERFIL", image: "/caps/obsidian-side.png" },
  { name: "REVERSO", image: "/caps/obsidian-back.png" },
];

export default function Home() {
  const [variant, setVariant] = useState("OBSIDIAN");
  const [submitted, setSubmitted] = useState(false);
  const [scrollProgress, setScrollProgress] = useState(0);
  const [revealProgress, setRevealProgress] = useState(0);
  const showcaseRef = useRef<HTMLElement>(null);

  useEffect(() => {
    let frame = 0;
    const updateProgress = () => {
      const section = showcaseRef.current;
      if (!section) return;
      const bounds = section.getBoundingClientRect();
      const available = Math.max(1, bounds.height - window.innerHeight);
      const next = Math.min(1, Math.max(0, -bounds.top / available));
      // La pieza inicial empieza a revelarse antes de que la sección se fije.
      const earlyReveal = Math.min(1, Math.max(0, (-bounds.top + 180) / available));
      setScrollProgress((current) => Math.abs(current - next) > 0.002 ? next : current);
      setRevealProgress((current) => Math.abs(current - earlyReveal) > 0.002 ? earlyReveal : current);
    };
    const onScroll = () => { cancelAnimationFrame(frame); frame = requestAnimationFrame(updateProgress); };
    updateProgress();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    return () => { cancelAnimationFrame(frame); window.removeEventListener("scroll", onScroll); window.removeEventListener("resize", onScroll); };
  }, []);

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitted(true);
  }

  const activeVariant = variants[Math.min(2, Math.floor(scrollProgress * 3))];

  return (
    <main style={{ "--scroll": scrollProgress } as React.CSSProperties}>
      <nav><span className="wordmark">SON OF GOD</span><span className="edition">DROP 01 / MÉXICO</span></nav>
      <section className="hero">
        <div className="ambient ambient-one" /><div className="ambient ambient-two" />
        <div className="hero-copy">
          <p className="eyebrow">ACCESO ANTICIPADO — 10 LUGARES</p>
          <h1>Elegidos antes<br />del lanzamiento.</h1>
          <p className="intro">El primer drop de SON OF GOD. Regístrate, recibe tu código y entra primero cuando la tienda abra.</p>
          <a href="#registro" className="cta">QUIERO MI ACCESO <span>↓</span></a>
        </div>
        <div className={`product-stage ${variants.find((item) => item.name === variant)?.className}`} aria-label="Gorra SON OF GOD edición limitada">
          <div className="hero-render"><Image src="/caps/obsidian.png" alt="Gorra SON OF GOD Obsidian" fill priority sizes="(max-width: 700px) 88vw, 42vw" /></div>
          <div className="brand-stamp"><span>SOG</span><small>SON OF GOD<br />DROP 01</small></div>
          <p className="stage-label">{variant} / 01</p>
        </div>
      </section>
      <section className="showcase" ref={showcaseRef} aria-label="Explora las gorras del Drop 01">
        <div className="showcase-sticky">
          <div className="showcase-copy"><p className="eyebrow">DROP 01 / {activeVariant.name}</p><h2>Hecha para<br />cada ángulo.</h2></div>
          <div className="scroll-product" aria-hidden="true">
            <CapViewer progress={scrollProgress} revealProgress={revealProgress} />
            <div className="orbit orbit-one" /><div className="orbit orbit-two" />
          </div>
          <div className="showcase-status"><span>{String(Math.min(3, Math.floor(scrollProgress * 3) + 1)).padStart(2, "0")} / 03</span><strong>{activeVariant.name} / 01</strong><span>{activeVariant.detail}</span></div>
        </div>
      </section>
      <section id="registro" className="register">
        <div className="register-heading"><p className="eyebrow">LA LISTA</p><h2>Tu lugar<br />no se repite.</h2><p>Solo 10 accesos. Al registrarte recibirás un código personal por correo para la siguiente fase.</p></div>
        {submitted ? <div className="success glass"><p className="eyebrow">ACCESO RESERVADO</p><h3>Revisa tu correo.</h3><p>Tu código de acceso está en camino. Guárdalo para el Drop 01.</p></div> :
        <form className="glass" onSubmit={submit}>
          <label>Nombre<input required name="name" placeholder="Tu nombre" /></label>
          <label>Correo electrónico<input required type="email" name="email" placeholder="tu@correo.com" /></label>
          <label>Celular<input required type="tel" name="phone" placeholder="55 0000 0000" /></label>
          <fieldset><legend>Elige tu pieza</legend><div className="variants">{variants.map((item) => <button type="button" className={variant === item.name ? "active" : ""} key={item.name} onClick={() => setVariant(item.name)}><span className={`swatch ${item.className}`} />{item.name}<small>{item.detail}</small></button>)}</div></fieldset>
          <button className="submit" type="submit">RECIBIR MI CÓDIGO <span>→</span></button><p className="fine-print">Envíos exclusivos a México. Al registrarte aceptas recibir información sobre este drop.</p>
        </form>}
      </section>
      <footer><span>SON OF GOD © 2026</span><span>HECHO PARA MÉXICO</span></footer>
    </main>
  );
}
