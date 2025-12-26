import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: 'Comprehensive Robotics Curriculum',
    Svg: require('@site/static/img/undraw_docusaurus_mountain.svg').default,
    description: (
      <>
        Learn the complete stack of humanoid robotics development from ROS 2 fundamentals
        to advanced AI integration with NVIDIA Isaac™ and Vision-Language-Action systems.
      </>
    ),
  },
  {
    title: 'Hands-On Learning Approach',
    Svg: require('@site/static/img/undraw_docusaurus_tree.svg').default,
    description: (
      <>
        Build practical skills through real-world projects and simulations with
        Gazebo, Unity, and digital twin technologies.
      </>
    ),
  },
  {
    title: 'Cutting-Edge Technologies',
    Svg: require('@site/static/img/undraw_docusaurus_react.svg').default,
    description: (
      <>
        Master state-of-the-art tools and frameworks including ROS 2, NVIDIA Isaac™,
        and advanced AI systems for robotics.
      </>
    ),
  },
];

function Feature({Svg, title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
