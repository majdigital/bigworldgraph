export const fallback = 'fr';

export const data = {
  fr: {
    categories: {
      label: 'Catégories',
      Affair: 'Affaire',
      Politician: 'Politicien',
      Party: 'Parti politique',
      Company: 'Entreprise',
      Organization: 'Organisation',
      Media: 'Média',
      Person: 'Personne',
      Journalist: 'Journaliste',
    },
  },
  en: {
    categories: {
      label: 'Categories',
      Affair: 'Affair',
      Politician: 'Politician',
      Party: 'Party',
      Company: 'Company',
      Organization: 'Organization',
      Media: 'Media',
      Person: 'Person',
      Journalist: 'Journalist',
    },
  },
};

export default locale => ({
  ...(data[locale] || data[fallback]),
});
