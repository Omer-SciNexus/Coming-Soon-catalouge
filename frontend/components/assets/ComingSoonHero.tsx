import styles from "./ComingSoonHero.module.css";

// image_* exist from version 1.1.0 and document_* from 1.2.0. Older pages never send them, so they look the same.
type Props = {
  heading: string;
  description: string;
  image_url?: string;
  image_alt?: string;
  document_url?: string;
  document_label?: string;
};

// Django already checked the pattern on save. The renderer checks again and fails closed:
// only http(s) addresses and same-site paths ("/media/...", "/documents/...") are used, anything else is ignored.
export function isSafeUrl(url: unknown): url is string {
  return typeof url === "string" && /^(https?:\/\/|\/(?!\/))\S+$/.test(url);
}

export function ComingSoonHero({ heading, description, image_url, image_alt, document_url, document_label }: Props) {
  const image = isSafeUrl(image_url) ? image_url : null;
  const document = isSafeUrl(document_url) ? document_url : null;
  return (
    <section className={image ? `${styles.hero} ${styles.withImage}` : styles.hero}>
      <div>
        <h2 className={styles.heading}>{heading}</h2>
        <p className={styles.description}>{description}</p>
        {document && (
          <a className={styles.document} href={document} target="_blank" rel="noopener noreferrer">
            <svg aria-hidden="true" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 4v11m0 0-4.5-4.5M12 15l4.5-4.5M5 20h14" />
            </svg>
            {document_label || "Download"}
          </a>
        )}
      </div>
      {/* A plain <img>: the address comes from the CMS at runtime, so next/image's build-time host list does not fit. */}
      {image && <img className={styles.image} src={image} alt={image_alt ?? ""} />}
    </section>
  );
}
