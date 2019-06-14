export const fallback = 'fr';

export const data = {
  fr: {
    wikipediaArticles: 'Articles Wikipédia',
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
    wikipediaArticles: 'Wikipedia articles',
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
