<?php
/**
 * Template Name: Careers
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }
get_header();
?>

<main id="primary" class="site-main container mx-auto px-4 py-8">
  <nav class="text-sm text-muted-foreground mb-2" aria-label="Breadcrumbs">
    <a class="hover:underline" href="<?php echo esc_url(home_url('/')); ?>"><?php esc_html_e('Home', 'retail-trade-scanner'); ?></a>
    <span> / </span>
    <span aria-current="page"><?php esc_html_e('Careers', 'retail-trade-scanner'); ?></span>
  </nav>
  
  <header class="mb-6">
    <h1 class="text-3xl font-bold leading-tight"><?php esc_html_e('Join Our Team', 'retail-trade-scanner'); ?></h1>
    <p class="mt-2 text-muted-foreground max-w-2xl"><?php esc_html_e('Help us build the future of retail trading technology and empower individual investors worldwide', 'retail-trade-scanner'); ?></p>
  </header>

  <section class="grid gap-6 py-6">
    <?php get_template_part('template-parts/components/card', null, [
      'title' => __('Why Work With Us?', 'retail-trade-scanner'),
      'content' => '<div class="grid gap-4 md:grid-cols-2">'
        . '<div>'
        . '<h4 class="font-semibold mb-2">🚀 ' . __('Innovation First', 'retail-trade-scanner') . '</h4>'
        . '<p class="text-sm">' . __('Work on cutting-edge fintech solutions that directly impact how retail investors make decisions.', 'retail-trade-scanner') . '</p>'
        . '</div>'
        . '<div>'
        . '<h4 class="font-semibold mb-2">🌱 ' . __('Growth Opportunities', 'retail-trade-scanner') . '</h4>'
        . '<p class="text-sm">' . __('Continuous learning environment with opportunities to expand your skills and advance your career.', 'retail-trade-scanner') . '</p>'
        . '</div>'
        . '<div>'
        . '<h4 class="font-semibold mb-2">💪 ' . __('Work-Life Balance', 'retail-trade-scanner') . '</h4>'
        . '<p class="text-sm">' . __('Flexible working arrangements, competitive benefits, and a culture that values your well-being.', 'retail-trade-scanner') . '</p>'
        . '</div>'
        . '<div>'
        . '<h4 class="font-semibold mb-2">🌍 ' . __('Remote-First', 'retail-trade-scanner') . '</h4>'
        . '<p class="text-sm">' . __('Join our distributed team and work from anywhere while collaborating with talented professionals globally.', 'retail-trade-scanner') . '</p>'
        . '</div>'
        . '</div>',
    ]); ?>

    <div class="grid gap-6 lg:grid-cols-2">
      <?php get_template_part('template-parts/components/card', null, [
        'title' => __('Current Openings', 'retail-trade-scanner'),
        'content' => '<div class="space-y-4">'
          . '<div class="border-l-4 border-primary pl-4">'
          . '<h4 class="font-semibold">' . __('Senior Backend Developer', 'retail-trade-scanner') . '</h4>'
          . '<p class="text-sm text-muted-foreground mb-2">' . __('Full-time • Remote • $120k - $160k', 'retail-trade-scanner') . '</p>'
          . '<p class="text-sm">' . __('Build and scale our real-time data processing systems using Python, FastAPI, and modern cloud infrastructure.', 'retail-trade-scanner') . '</p>'
          . '<a href="#" class="inline-flex items-center text-primary hover:underline text-sm mt-2">' . __('Apply Now →', 'retail-trade-scanner') . '</a>'
          . '</div>'
          
          . '<div class="border-l-4 border-primary pl-4">'
          . '<h4 class="font-semibold">' . __('Frontend React Developer', 'retail-trade-scanner') . '</h4>'
          . '<p class="text-sm text-muted-foreground mb-2">' . __('Full-time • Remote • $100k - $140k', 'retail-trade-scanner') . '</p>'
          . '<p class="text-sm">' . __('Create beautiful, responsive user interfaces that make complex financial data accessible and actionable.', 'retail-trade-scanner') . '</p>'
          . '<a href="#" class="inline-flex items-center text-primary hover:underline text-sm mt-2">' . __('Apply Now →', 'retail-trade-scanner') . '</a>'
          . '</div>'
          
          . '<div class="border-l-4 border-primary pl-4">'
          . '<h4 class="font-semibold">' . __('Data Engineer', 'retail-trade-scanner') . '</h4>'
          . '<p class="text-sm text-muted-foreground mb-2">' . __('Full-time • Remote • $110k - $150k', 'retail-trade-scanner') . '</p>'
          . '<p class="text-sm">' . __('Design and maintain data pipelines that process millions of market data points in real-time.', 'retail-trade-scanner') . '</p>'
          . '<a href="#" class="inline-flex items-center text-primary hover:underline text-sm mt-2">' . __('Apply Now →', 'retail-trade-scanner') . '</a>'
          . '</div>'
          
          . '<div class="text-center mt-6">'
          . '<p class="text-sm text-muted-foreground mb-3">' . __('Don\'t see a perfect fit? We\'re always looking for talented individuals.', 'retail-trade-scanner') . '</p>'
          . '<a href="' . esc_url(home_url('/contact/')) . '" class="inline-flex items-center justify-center px-4 py-2 rounded-md bg-primary text-primary-foreground hover:shadow-sm transition">' . __('Send Us Your Resume', 'retail-trade-scanner') . '</a>'
          . '</div>'
          . '</div>',
      ]); ?>

      <?php get_template_part('template-parts/components/card', null, [
        'title' => __('Our Tech Stack', 'retail-trade-scanner'),
        'content' => '<div class="space-y-4">'
          . '<div>'
          . '<h4 class="font-semibold mb-2">' . __('Backend & APIs', 'retail-trade-scanner') . '</h4>'
          . '<div class="flex flex-wrap gap-2">'
          . '<span class="inline-flex items-center px-2 py-1 rounded-full bg-muted/30 text-xs">Python</span>'
          . '<span class="inline-flex items-center px-2 py-1 rounded-full bg-muted/30 text-xs">FastAPI</span>'
          . '<span class="inline-flex items-center px-2 py-1 rounded-full bg-muted/30 text-xs">PostgreSQL</span>'
          . '<span class="inline-flex items-center px-2 py-1 rounded-full bg-muted/30 text-xs">Redis</span>'
          . '<span class="inline-flex items-center px-2 py-1 rounded-full bg-muted/30 text-xs">Docker</span>'
          . '</div>'
          . '</div>'
          
          . '<div>'
          . '<h4 class="font-semibold mb-2">' . __('Frontend & UI', 'retail-trade-scanner') . '</h4>'
          . '<div class="flex flex-wrap gap-2">'
          . '<span class="inline-flex items-center px-2 py-1 rounded-full bg-muted/30 text-xs">React</span>'
          . '<span class="inline-flex items-center px-2 py-1 rounded-full bg-muted/30 text-xs">TypeScript</span>'
          . '<span class="inline-flex items-center px-2 py-1 rounded-full bg-muted/30 text-xs">Tailwind CSS</span>'
          . '<span class="inline-flex items-center px-2 py-1 rounded-full bg-muted/30 text-xs">Chart.js</span>'
          . '</div>'
          . '</div>'
          
          . '<div>'
          . '<h4 class="font-semibold mb-2">' . __('Infrastructure', 'retail-trade-scanner') . '</h4>'
          . '<div class="flex flex-wrap gap-2">'
          . '<span class="inline-flex items-center px-2 py-1 rounded-full bg-muted/30 text-xs">AWS</span>'
          . '<span class="inline-flex items-center px-2 py-1 rounded-full bg-muted/30 text-xs">Kubernetes</span>'
          . '<span class="inline-flex items-center px-2 py-1 rounded-full bg-muted/30 text-xs">GitHub Actions</span>'
          . '<span class="inline-flex items-center px-2 py-1 rounded-full bg-muted/30 text-xs">Monitoring</span>'
          . '</div>'
          . '</div>'
          
          . '<div class="mt-6 p-4 bg-muted/30 rounded-lg">'
          . '<p class="text-sm"><strong>' . __('Learning & Development:', 'retail-trade-scanner') . '</strong> ' . __('We invest in our team\'s growth with conference tickets, online courses, and dedicated learning time.', 'retail-trade-scanner') . '</p>'
          . '</div>'
          . '</div>',
      ]); ?>
    </div>
  </section>
</main>

<?php get_footer(); ?>