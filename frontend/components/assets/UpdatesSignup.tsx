"use client";

import { useState, type FormEvent } from "react";
import styles from "./UpdatesSignup.module.css";

type Props = { label: string };

export function UpdatesSignup({ label }: Props) {
  const [sent, setSent] = useState(false);

  // In the real system this form posts the email to a Django endpoint.
  // This demo has no signup backend, so it only shows a confirmation.
  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSent(true);
  }

  if (sent) return <p className={styles.thanks}>Thanks! We will let you know.</p>;

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <input className={styles.input} type="email" name="email" placeholder="you@example.com" required />
      <button className={styles.button} type="submit">
        {label}
      </button>
    </form>
  );
}
