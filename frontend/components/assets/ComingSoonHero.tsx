import styles from "./ComingSoonHero.module.css";

type Props = { heading: string; description: string };

export function ComingSoonHero({ heading, description }: Props) {
  return (
    <section className={styles.hero}>
      <h2 className={styles.heading}>{heading}</h2>
      <p className={styles.description}>{description}</p>
    </section>
  );
}
